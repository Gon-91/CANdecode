from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QLineEdit, QPushButton, QComboBox,
    QSpinBox, QScrollArea
)
from PyQt5.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar


class DlcGraphWidget(QWidget):
    """
    CAN / CAN FD DLC 시각화 위젯 (CAN Layer Layout)
    - 세로: 바이트
    - 가로: 비트 8개 (b7~b0)
    - DLC만큼 바이트 표시
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.df = pd.DataFrame()
        self.can_id = None
        self.dlc = 0
        self.data_cols = []

        self.factor = 1.0
        self.offset = 0.0

        self.selected_bits = []  # (byte_idx, bit_idx)
        self._auto_updating_bits = False

        self.init_ui()

    # ---------------- UI 초기화 ----------------
    def init_ui(self):
        layout = QVBoxLayout(self)

        # 정보 표시
        self.info_label = QLabel("CAN ID: N/A | DLC: 0")
        layout.addWidget(self.info_label)

        # Factor / Offset
        fo_layout = QHBoxLayout()
        self.factor_input = QLineEdit("1")
        self.offset_input = QLineEdit("0")
        apply_btn = QPushButton("적용")
        apply_btn.clicked.connect(self.apply_factor_offset)
        fo_layout.addWidget(QLabel("Factor"))
        fo_layout.addWidget(self.factor_input)
        fo_layout.addWidget(QLabel("Offset"))
        fo_layout.addWidget(self.offset_input)
        fo_layout.addWidget(apply_btn)
        layout.addLayout(fo_layout)

        # 비트 단위 수동 입력
        bit_layout = QHBoxLayout()
        self.bit_start_spin = QSpinBox()
        self.bit_start_spin.setRange(0, 511)
        self.bit_start_spin.valueChanged.connect(self.plot_graphs)
        self.bit_length_spin = QSpinBox()
        self.bit_length_spin.setRange(1, 512)
        self.bit_length_spin.valueChanged.connect(self.plot_graphs)
        bit_layout.addWidget(QLabel("시작 비트"))
        bit_layout.addWidget(self.bit_start_spin)
        bit_layout.addWidget(QLabel("비트 길이"))
        bit_layout.addWidget(self.bit_length_spin)
        layout.addLayout(bit_layout)

        # 엔디안 선택
        endian_layout = QHBoxLayout()
        self.endian_combo = QComboBox()
        self.endian_combo.addItems(["Big Endian", "Little Endian"])
        self.endian_combo.currentIndexChanged.connect(self.plot_graphs)
        endian_layout.addWidget(QLabel("Endian"))
        endian_layout.addWidget(self.endian_combo)
        layout.addLayout(endian_layout)

        # 바이트×비트 테이블 (CAN Layer Layout)
        self.bit_table = QTableWidget(0, 8)  # 초기 0행, 8열
        self.bit_table.setHorizontalHeaderLabels([f"b{7-i}" for i in range(8)])
        self.bit_table.verticalHeader().setVisible(True)
        self.bit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bit_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bit_table.cellClicked.connect(self.on_bit_clicked)
        table_scroll = QScrollArea()
        table_scroll.setWidgetResizable(True)
        table_scroll.setWidget(self.bit_table)
        table_scroll.setFixedHeight(300)
        layout.addWidget(table_scroll)

        # 그래프 영역
        self.canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        self.ax = self.canvas.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self._init_empty_graph()

    def _init_empty_graph(self):
        self.ax.set_title("CAN / CAN FD DLC Graph (비트 단위)")
        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel("값 (10진수)")
        self.ax.grid(True)
        self.canvas.draw()

    # ---------------- 데이터 로드 ----------------
    def update_graph(self, df: pd.DataFrame, can_id: str):
        if df.empty:
            return
        filtered = df[df["can_id"] == can_id].reset_index(drop=True)
        if filtered.empty:
            return

        self.df = filtered
        self.can_id = can_id
        self.dlc = int(self.df["dlc"].iloc[0])
        self.data_cols = [str(i) for i in range(self.dlc)]

        # 테이블 초기화
        self.bit_table.setRowCount(self.dlc)
        self.bit_table.setVerticalHeaderLabels([f"B{i}" for i in range(self.dlc)])

        for r in range(self.dlc):
            for c in range(8):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.bit_table.setItem(r, c, item)

        self.selected_bits.clear()
        self.info_label.setText(f"CAN ID: {self.can_id} | DLC: {self.dlc} bytes")
        self._init_empty_graph()

    # ---------------- UI 이벤트 ----------------
    def on_bit_clicked(self, row, col):
        bit = (row, col)
        item = self.bit_table.item(row, col)
        if bit in self.selected_bits:
            self.selected_bits.remove(bit)
            item.setText("")
            item.setBackground(Qt.white)
        else:
            self.selected_bits.append(bit)
            item.setText("✔")
            item.setBackground(Qt.gray)

        # 자동 비트 범위 계산
        self.update_bit_range()
        self.plot_graphs()

    def update_bit_range(self):
        if not self.selected_bits:
            return
        min_byte = min(b for b, _ in self.selected_bits)
        max_byte = max(b for b, _ in self.selected_bits)
        min_bit = min(b for _, b in self.selected_bits)
        max_bit = max(b for _, b in self.selected_bits)
        start_bit = min_byte * 8 + min_bit
        end_bit = max_byte * 8 + max_bit
        self._auto_updating_bits = True
        self.bit_start_spin.setValue(start_bit)
        self.bit_length_spin.setValue(end_bit - start_bit + 1)
        self._auto_updating_bits = False

    def apply_factor_offset(self):
        try:
            self.factor = float(self.factor_input.text())
        except:
            self.factor = 1.0
        try:
            self.offset = float(self.offset_input.text())
        except:
            self.offset = 0.0
        self.plot_graphs()

    # ---------------- 내부 계산 ----------------
    def compute_bits_value(self, row, bits_start, bits_len, endian="Big Endian"):
        bytes_data = []
        for i in range(self.dlc):
            try:
                val = row.get(str(i), 0)
                v = int(val, 16) if isinstance(val, str) else int(val)
            except:
                v = 0
            bytes_data.append(v)
        if endian == "Little Endian":
            bytes_data = list(reversed(bytes_data))

        # 전체 비트 배열
        bit_array = []
        for byte in bytes_data:
            bit_array.extend([(byte >> i) & 1 for i in range(7, -1, -1)])

        selected_bits = bit_array[bits_start:bits_start + bits_len]
        value = 0
        for b in selected_bits:
            value = (value << 1) | b
        return value

    # ---------------- 그래프 ----------------
    def plot_graphs(self):
        if self._auto_updating_bits:
            return
        self.ax.clear()
        if self.df.empty:
            self._init_empty_graph()
            return

        bits_start = self.bit_start_spin.value()
        bits_len = self.bit_length_spin.value()
        endian = self.endian_combo.currentText()
        ts = self.df["timestamp"] if "timestamp" in self.df.columns else range(len(self.df))

        try:
            y = self.df.apply(lambda row: self.compute_bits_value(row, bits_start, bits_len, endian), axis=1)
            y = y * self.factor + self.offset
            self.ax.plot(ts, y, color="blue", linewidth=2)
        except Exception as e:
            print(f"[WARN] Plot error: {e}")

        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel(f"값 ({bits_len} bits)")
        self.ax.set_title(f"CAN {self.can_id} ({endian})")
        self.ax.grid(True)
        self.canvas.draw()
