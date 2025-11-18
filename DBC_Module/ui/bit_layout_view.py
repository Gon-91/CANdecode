# ui/bit_layout_view.py
from PySide6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QSizePolicy, QAbstractItemView
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QBrush, QCursor


def expand_intel(start_bit: int, length: int, max_bits: int = None):
    """Intel / little-endian expansion: consecutive global bits start..start+len-1"""
    bits = [start_bit + i for i in range(length)]
    if max_bits is not None:
        bits = [b for b in bits if 0 <= b < max_bits]
    return bits


def expand_motorola(start_bit: int, length: int, max_bits: int = None):
    """
    Motorola (CANalyzer / Vector DBC++ visualization style).
    Start at (byte = start_bit//8, bit = start_bit%8), then decrease bit.
    If bit < 0 -> bit = 7 and byte += 1 (move to next byte).
    """
    bits = []
    byte = start_bit // 8
    bit = start_bit % 8
    for _ in range(length):
        g = byte * 8 + bit
        if max_bits is not None and (g < 0 or g >= max_bits):
            break
        bits.append(g)
        bit -= 1
        if bit < 0:
            bit = 7
            byte += 1
    return bits


def expand_signal_bits(sig, max_bits: int):
    """Dispatch expansion depending on sig.byte_order (1=intel, 0=motorola)."""
    if sig.byte_order == 1:
        return expand_intel(sig.start_bit, sig.length, max_bits)
    return expand_motorola(sig.start_bit, sig.length, max_bits)


class BitTableWidget(QTableWidget):
    """
    Internal QTableWidget subclass that handles mouse interactions:
    - Click selects signal
    - Drag (body) moves signal
    - Drag (edge) resizes left/right
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.viewport().setCursor(QCursor(Qt.ArrowCursor))

        # Drag state
        self._dragging = False
        self._drag_mode = None  # 'move' | 'resize_left' | 'resize_right'
        self._drag_sig = None
        self._drag_click_index = 0
        self._drag_start_pos = QPoint()
        # 테이블 배경 검은색
        self.setStyleSheet("""
            QTableWidget {
                background-color: black;
                gridline-color: gray;       /* 셀 구분선 색상 */
            }
        """)
    # helpers
    def cell_to_global(self, row: int, col: int) -> int:
        """Convert table row,col -> global bit index (row=byte, col visual 7->0)."""
        bit_in_byte = 7 - col
        return row * 8 + bit_in_byte

    def global_to_cell(self, global_bit: int):
        row = global_bit // 8
        bit_in_byte = global_bit % 8
        col = 7 - bit_in_byte
        return row, col

    def pos_to_cell(self, pos):
        col = self.columnAt(pos.x())
        row = self.rowAt(pos.y())
        if row < 0 or col < 0:
            return None, None
        return row, col

    # mouse events
    def mousePressEvent(self, event):
        row, col = self.pos_to_cell(event.pos())
        parent = self.parent()  # BitTableView
        if row is None or parent is None or not parent.message:
            super().mousePressEvent(event)
            return

        g = self.cell_to_global(row, col)
        # find signal that contains g
        sig = None
        sig_bits = None
        max_bits = parent.message.dlc * 8
        for s in parent.message.signals:
            bits = expand_signal_bits(s, max_bits)
            if g in bits:
                sig = s
                sig_bits = bits
                break

        if sig is None:
            # deselect
            parent.set_selected_signal(None)
            super().mousePressEvent(event)
            return

        # Select the signal in parent
        parent.set_selected_signal(sig)

        # Determine click index inside signal bits (visual order as expanded list)
        try:
            idx = sig_bits.index(g)
        except ValueError:
            idx = 0

        # Determine edge vs body by index
        # Left edge -> idx == 0 (first visual bit)
        # Right edge -> idx == len(bits)-1
        # Use tolerance by cell width if needed (we use index test for simplicity)
        if idx == 0:
            self._drag_mode = 'resize_left'
        elif idx == len(sig_bits) - 1:
            self._drag_mode = 'resize_right'
        else:
            self._drag_mode = 'move'

        # start drag state
        self._dragging = True
        self._drag_sig = sig
        self._drag_click_index = idx
        self._drag_start_pos = event.pos()

        # call base so default focus behavior still works
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        parent = self.parent()
        if not parent or not parent.message:
            super().mouseMoveEvent(event)
            return

        # Hover cursor behavior when not dragging
        if not self._dragging or not self._drag_sig:
            # change cursor if over a signal cell
            row, col = self.pos_to_cell(event.pos())
            if row is None:
                self.viewport().setCursor(QCursor(Qt.ArrowCursor))
                super().mouseMoveEvent(event)
                return
            g = self.cell_to_global(row, col)
            max_bits = parent.message.dlc * 8
            over_sig = None
            for s in parent.message.signals:
                if g in expand_signal_bits(s, max_bits):
                    over_sig = s
                    break
            if over_sig:
                self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
            else:
                self.viewport().setCursor(QCursor(Qt.ArrowCursor))
            super().mouseMoveEvent(event)
            return

        # Dragging in progress
        sig = self._drag_sig
        max_bits = parent.message.dlc * 8
        orig_bits = expand_signal_bits(sig, max_bits)
        if not orig_bits:
            return

        mode = self._drag_mode
        item = self.table().itemAt(event.pos()) if hasattr(self, "table") else self.itemAt(event.pos())
        row, col = self.pos_to_cell(event.pos())
        if row is None:
            return
        g_under = self.cell_to_global(row, col)

        if mode == 'move':
            # For Intel: new_start = g_under - click_index
            # For Motorola: find candidate start s.t. expanded[start][click_index] == g_under
            if sig.byte_order == 1:
                new_start = g_under - self._drag_click_index
            else:
                # search candidate start nearby
                new_start = sig.start_bit  # fallback
                # search candidate range
                low = max(0, g_under - 16)
                high = min(max_bits - 1, g_under + 16)
                found = False
                for cand in range(low, high + 1):
                    cand_bits = expand_motorola(cand, sig.length, max_bits)
                    if len(cand_bits) == sig.length and cand_bits[self._drag_click_index] == g_under:
                        new_start = cand
                        found = True
                        break
                if not found:
                    # fallback approximation
                    new_start = max(0, min(sig.start_bit + (g_under - self._drag_start_pos.x()) // max(1, self.columnWidth(0)), max_bits - sig.length))
            # clamp
            new_start = max(0, min(max_bits - sig.length, new_start))
            if new_start != sig.start_bit:
                sig.start_bit = new_start

        elif mode == 'resize_left':
            # keep right endpoint fixed, change start & length
            orig_first = orig_bits[0]
            orig_last = orig_bits[-1]
            if sig.byte_order == 1:
                # Intel: new_first = g_under (approx)
                new_first = g_under
                new_len = orig_last - new_first + 1
                if new_len >= 1:
                    new_first = max(0, new_first)
                    new_len = min(max_bits - new_first, new_len)
                    sig.start_bit = new_first
                    sig.length = new_len
            else:
                # Motorola: make g_under the new first if reachable
                # compute steps from g_under forward and see when we hit orig_last
                # brute-force attempt
                found = False
                for cand in range(max(0, g_under - 16), min(max_bits, g_under + 16)):
                    seq = expand_motorola(cand, sig.length + 64, max_bits)
                    if seq and seq[-1] == orig_last:
                        new_len = seq.index(orig_last) + 1
                        sig.start_bit = cand
                        sig.length = new_len
                        found = True
                        break
                if not found:
                    # fallback: set start to g_under and recompute length heuristic
                    sig.start_bit = max(0, min(g_under, max_bits - 1))
                    # recalc length as steps to orig_last
                    cnt = 0
                    cur = sig.start_bit
                    while cnt < max_bits:
                        if cur == orig_last:
                            sig.length = cnt + 1
                            break
                        byte = cur // 8
                        bit = cur % 8
                        bit -= 1
                        if bit < 0:
                            bit = 7
                            byte += 1
                        cur = byte * 8 + bit
                        cnt += 1

        elif mode == 'resize_right':
            # change length, keep first fixed
            orig_first = orig_bits[0]
            if sig.byte_order == 1:
                new_len = g_under - orig_first + 1
                if new_len >= 1:
                    new_len = max(1, min(max_bits - orig_first, new_len))
                    sig.length = new_len
            else:
                # count steps from orig_first until g_under encountered
                cnt = 0
                cur = orig_first
                new_len = None
                while cnt < max_bits:
                    if cur == g_under:
                        new_len = cnt + 1
                        break
                    byte = cur // 8
                    bit = cur % 8
                    bit -= 1
                    if bit < 0:
                        bit = 7
                        byte += 1
                    cur = byte * 8 + bit
                    cnt += 1
                if new_len is not None:
                    sig.length = max(1, min(max_bits - sig.start_bit, new_len))

        # after-change: notify parent to repaint table
        if hasattr(parent, "_after_sig_change"):
            parent._after_sig_change(sig)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._drag_mode = None
        self._drag_sig = None
        super().mouseReleaseEvent(event)


class BitTableView(QWidget):
    """
    Public widget to integrate into MainWindow.
    API:
      - set_message(msg)
      - set_selected_signal(sig)
      - signal_changed_callback = callable(sig)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.message = None
        self.selected_signal = None
        self._signal_changed_callback = None

        self.table = BitTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setRowCount(1)
        self.table.setHorizontalHeaderLabels([str(7 - i) for i in range(8)])
        # visual defaults
        for c in range(8):
            self.table.setColumnWidth(c, 75)
        self.table.verticalHeader().setDefaultSectionSize(75)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

    # public API
    def set_message(self, msg):
        """Set message model (expects msg.dlc and msg.signals list)."""
        self.message = msg
        rows = max(1, msg.dlc)
        self.table.setRowCount(rows)
        # set vertical labels
        self.table.setVerticalHeaderLabels([f"B{r}" for r in range(rows)])
        # ensure items exist
        for r in range(rows):
            for c in range(8):
                if self.table.item(r, c) is None:
                    self.table.setItem(r, c, QTableWidgetItem(""))
        self._refresh_table()

    def set_selected_signal(self, sig):
        self.selected_signal = sig
        self._refresh_table()

    @property
    def signal_changed_callback(self):
        return self._signal_changed_callback

    @signal_changed_callback.setter
    def signal_changed_callback(self, cb):
        self._signal_changed_callback = cb

    # internal helper called by BitTableWidget after modifying a signal
    def _after_sig_change(self, sig):
        # refresh visuals
        self._refresh_table()
        # call external callback
        if callable(self._signal_changed_callback):
            self._signal_changed_callback(sig)

    def _refresh_table(self):
        if not self.message:
            return
        max_bits = self.message.dlc * 8
        # clear cell text/background
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                it = self.table.item(r, c)
                if it is None:
                    it = QTableWidgetItem("")
                    self.table.setItem(r, c, it)
                it.setText("")
                it.setBackground(QBrush(Qt.black))

        # paint signals
        for sig in self.message.signals:
            bits = expand_signal_bits(sig, max_bits)
            if not bits:
                continue
            # pick color
            col = QColor(150, 200, 255, 140)
            if hasattr(sig, "color") and sig.color:
                try:
                    col = QColor(sig.color) if not isinstance(sig.color, QColor) else sig.color
                except Exception:
                    col = QColor(150, 200, 255, 140)
            # emphasize selected signal
            if sig == self.selected_signal:
                col = QColor(255, 220, 140, 180)
            brush = QBrush(col)
            for i, g in enumerate(bits):
                if g < 0 or g >= max_bits:
                    continue
                r, c = self.table.rowCount() - 1, 0  # default fallback (will be replaced)
                r, c = g // 8, 7 - (g % 8)
                it = self.table.item(r, c)
                if it is None:
                    it = QTableWidgetItem("")
                    self.table.setItem(r, c, it)
                # Show name only on first visual bit of the signal
                if i == 0:
                    it.setText(sig.name)
                it.setBackground(brush)
