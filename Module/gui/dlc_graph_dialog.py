from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
    QHeaderView, QHBoxLayout, QLineEdit, QPushButton, QComboBox
)
from PyQt5.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DlcGraphDialog(QDialog):
    """CAN ID DLC 시각화 (바이트 조합 전용, 엔디안 선택 + factor/offset 적용)"""
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CAN DLC 시각화")

        # DataFrame 복사
        self.df = df.copy().reset_index(drop=True)

        # 메시지 정보
        self.can_id = self.df["can_id"].iloc[0] if "can_id" in self.df.columns else "N/A"
        self.dlc = self.df["dlc"].iloc[0] if "dlc" in self.df.columns else len(self.df.columns)

        # 숫자 컬럼만 추출 (0,1,2,... 바이트)
        self.data_cols = [c for c in df.columns if str(c).isdigit()]

        # 기본 factor/offset
        self.factor = 1.0
        self.offset = 0.0

        # 선택 바이트 순서
        self.selected_bytes = []

        self.init_ui()
        self.plot_graphs()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # CAN ID / DLC 표시
        self.info_label = QLabel(f"CAN ID: {self.can_id} | DLC: {self.dlc}")
        layout.addWidget(self.info_label)

        # factor / offset 입력란
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

        # 엔디안 선택
        endian_layout = QHBoxLayout()
        self.endian_combo = QComboBox()
        self.endian_combo.addItems(["Big Endian", "Little Endian"])
        self.endian_combo.currentIndexChanged.connect(self.plot_graphs)
        endian_layout.addWidget(QLabel("Endian"))
        endian_layout.addWidget(self.endian_combo)
        layout.addLayout(endian_layout)

        # 바이트 선택 표
        self.selection_table = QTableWidget(1, len(self.data_cols))
        self.selection_table.setHorizontalHeaderLabels([f"B{i}" for i in range(len(self.data_cols))])
        self.selection_table.verticalHeader().setVisible(False)
        self.selection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.selection_table.cellClicked.connect(self.on_cell_clicked)
        layout.addWidget(self.selection_table)

        # 테이블 초기화
        for j, col in enumerate(self.data_cols):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignCenter)
            # DLC보다 긴 컬럼은 회색 처리 및 클릭 불가
            if j >= self.dlc:
                item.setFlags(Qt.NoItemFlags)
                item.setBackground(Qt.lightGray)
            self.selection_table.setItem(0, j, item)

        # 그래프 영역
        self.canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)

    def on_cell_clicked(self, row, column):
        """표 클릭 시 선택/해제 (선택 순서대로 조합)"""
        item = self.selection_table.item(row, column)
        if not item.flags() & Qt.ItemIsEnabled:
            return  # 클릭 불가
        col_name = self.data_cols[column]
        if col_name in self.selected_bytes:
            self.selected_bytes.remove(col_name)
            item.setText("")
            item.setBackground(Qt.white)
        else:
            self.selected_bytes.append(col_name)
            item.setText("✔")
            item.setBackground(Qt.gray)
        self.plot_graphs()

    def apply_factor_offset(self):
        """factor / offset 적용"""
        try:
            self.factor = float(self.factor_input.text())
        except Exception:
            self.factor = 1.0
        try:
            self.offset = float(self.offset_input.text())
        except Exception:
            self.offset = 0.0
        self.plot_graphs()

    def compute_decimal(self, row, byte_cols, endian="Big Endian"):
        """선택된 바이트 → 정수 조합 (엔디안 적용)"""
        bytes_list = []
        for c in byte_cols:
            try:
                b = row.get(c, 0)
                b_int = int(b, 16) if isinstance(b, str) else int(b)
            except Exception:
                b_int = 0
            bytes_list.append(b_int)

        if endian == "Little Endian":
            bytes_list = list(reversed(bytes_list))  # 순서 뒤집기

        value = 0
        for b in bytes_list:
            value = (value << 8) | b
        return value

    def plot_graphs(self):
        self.ax.clear()
        if not self.selected_bytes:
            self.canvas.draw()
            return

        ts = self.df["timestamp"] if "timestamp" in self.df.columns else range(len(self.df))
        endian = self.endian_combo.currentText()

        try:
            y = self.df.apply(lambda row: self.compute_decimal(row, self.selected_bytes, endian), axis=1)
            y = y * self.factor + self.offset
            self.ax.plot(ts, y, label="조합", color="blue", linewidth=2)
        except Exception as e:
            print(f"[WARN] Plot error: {e}")

        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel("값 (10진수)")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()
