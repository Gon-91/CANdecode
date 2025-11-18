from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QColorDialog, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class SignalTableView(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels(
            ["Name", "Start", "Len", "BO", "Type", "Fact", "Off", "Unit", "Color"]
        )

        # 폰트 설정
        font = QFont("Arial", 10)
        self.setFont(font)
        self.horizontalHeader().setFont(font)

        # Name 열 내용에 맞춰 자동 조정
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # 나머지 열은 화면 폭에 맞춰 Stretch
        for i in range(1, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.signals = []
        self.signal_changed_callback = None
        self.cellChanged.connect(self.on_cell_changed)

    def load_signals(self, signals):
        self.blockSignals(True)
        self.signals = signals
        self.setRowCount(len(signals))
        for row, sig in enumerate(signals):
            self.setItem(row, 0, QTableWidgetItem(sig.name))
            self.setItem(row, 1, QTableWidgetItem(str(sig.start_bit)))
            self.setItem(row, 2, QTableWidgetItem(str(sig.length)))

            cb_order = QComboBox()
            cb_order.addItems(["M", "I"])  # Motorola / Intel
            cb_order.setCurrentIndex(sig.byte_order)
            cb_order.currentIndexChanged.connect(lambda idx, s=sig: self.on_order_changed(s, idx))
            self.setCellWidget(row, 3, cb_order)

            cb_type = QComboBox()
            cb_type.addItems(["+", "-"])
            cb_type.setCurrentText(sig.value_type)
            cb_type.currentIndexChanged.connect(lambda idx, s=sig: self.on_type_changed(s, idx))
            self.setCellWidget(row, 4, cb_type)

            self.setItem(row, 5, QTableWidgetItem(str(sig.factor)))
            self.setItem(row, 6, QTableWidgetItem(str(sig.offset)))
            self.setItem(row, 7, QTableWidgetItem(sig.unit))

            # Color selector
            btn = QPushButton()
            btn.setStyleSheet(f"background-color:{sig.color.name()}")
            btn.clicked.connect(lambda checked, s=sig, b=btn: self.choose_color(s, b))
            self.setCellWidget(row, 8, btn)
        self.blockSignals(False)

    def choose_color(self, sig, btn):
        color = QColorDialog.getColor(sig.color, self)
        if color.isValid():
            sig.color = color
            btn.setStyleSheet(f"background-color:{color.name()}")
            if self.signal_changed_callback:
                self.signal_changed_callback(sig)

    def on_order_changed(self, sig, idx):
        sig.byte_order = idx
        if self.signal_changed_callback:
            self.signal_changed_callback(sig)

    def on_type_changed(self, sig, idx):
        sig.value_type = "+" if idx == 0 else "-"
        if self.signal_changed_callback:
            self.signal_changed_callback(sig)

    def on_cell_changed(self, row, col):
        sig = self.signals[row]
        if col == 0: sig.name = self.item(row, col).text()
        elif col == 1: sig.start_bit = int(self.item(row, col).text())
        elif col == 2: sig.length = int(self.item(row, col).text())
        elif col == 5: sig.factor = float(self.item(row, col).text())
        elif col == 6: sig.offset = float(self.item(row, col).text())
        elif col == 7: sig.unit = self.item(row, col).text()
        if self.signal_changed_callback:
            self.signal_changed_callback(sig)
