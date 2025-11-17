from PySide6.QtWidgets import QFrame, QSizePolicy
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QRect, QSize

class BitLayoutView(QFrame):
    def __init__(self):
        super().__init__()
        self.message = None
        self.selected_signal = None
        self.cell_w = 40
        self.cell_h = 25
        self.bits_per_byte = 8
        self.dragging_edge = None
        self.drag_start_x = 0
        self.signal_changed_callback = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_message(self, msg):
        self.message = msg
        self.selected_signal = None
        self.update()

    def set_selected_signal(self, sig):
        self.selected_signal = sig
        self.update()

    def paintEvent(self, event):
        if not self.message:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Draw grid
        for byte in range(self.message.dlc):
            for bit in range(self.bits_per_byte):
                x = bit * self.cell_w
                y = byte * self.cell_h
                rect = QRect(x, y, self.cell_w, self.cell_h)
                p.setPen(QPen(Qt.gray))
                p.drawRect(rect)
                p.drawText(rect, Qt.AlignCenter, f"B{byte}b{7-bit}")

        # Draw signals
        for sig in self.message.signals:
            self.draw_signal(p, sig)

    def draw_signal(self, p, sig):
        bits = []
        start = sig.start_bit
        length = sig.length
        if sig.byte_order == 1:  # Intel
            for i in range(length):
                bit_pos = start + i
                byte = bit_pos // 8
                bit = bit_pos % 8
                bits.append((byte, bit))
        else:  # Motorola
            for i in range(length):
                bit_pos = start - i
                byte = bit_pos // 8
                bit = bit_pos % 8
                bits.append((byte, bit))

        p.setPen(QPen(Qt.black))
        p.setBrush(sig.color)

        for byte, bit in bits:
            x = bit * self.cell_w
            y = byte * self.cell_h
            rect = QRect(x + 1, y + 1, self.cell_w - 2, self.cell_h - 2)
            p.drawRect(rect)

        # Signal name
        first_byte, first_bit = bits[0]
        x = first_bit * self.cell_w
        y = first_byte * self.cell_h
        p.drawText(QRect(x+2,y+2,max(10,length*self.cell_w),self.cell_h-4),
                   Qt.AlignVCenter | Qt.AlignLeft, sig.name)

    # Drag & Resize
    def mousePressEvent(self, event):
        if not self.selected_signal: return
        sig = self.selected_signal
        first_x = (sig.start_bit % self.bits_per_byte) * self.cell_w
        last_x = first_x + sig.length * self.cell_w
        if abs(event.x()-first_x)<5: self.dragging_edge='left'
        elif abs(event.x()-last_x)<5: self.dragging_edge='right'
        self.drag_start_x = event.x()

    def mouseMoveEvent(self,event):
        if not self.dragging_edge or not self.selected_signal: return
        dx_bits = round((event.x()-self.drag_start_x)/self.cell_w)
        sig = self.selected_signal
        if self.dragging_edge=='left':
            new_start=max(0,sig.start_bit+dx_bits)
            sig.length+=sig.start_bit-new_start
            sig.start_bit=new_start
        elif self.dragging_edge=='right':
            sig.length=max(1,sig.length+dx_bits)
        self.drag_start_x=event.x()
        self.update()
        if self.signal_changed_callback: self.signal_changed_callback(sig)

    def mouseReleaseEvent(self,event):
        self.dragging_edge=None

    def sizeHint(self):
        if not self.message: return QSize(400,300)
        width=self.bits_per_byte*self.cell_w
        height=max(300,self.message.dlc*self.cell_h)
        return QSize(width,height)
