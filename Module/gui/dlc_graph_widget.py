from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QLineEdit, QPushButton, QComboBox
)
from PyQt5.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)


class DlcGraphWidget(QWidget):
    """CAN ID DLC 시각화 위젯 (하나의 CAN ID만 표시)"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.df = pd.DataFrame()
        self.can_id = None
        self.dlc = 0
        self.data_cols = []

        # 기본 factor/offset
        self.factor = 1.0
        self.offset = 0.0

        # 선택 바이트
        self.selected_bytes = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # CAN ID / DLC 라벨
        self.info_label = QLabel("CAN ID: N/A | DLC: 0")
        layout.addWidget(self.info_label)

        # Factor / Offset 입력
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
        self.selection_table = QTableWidget(1, 0)
        self.selection_table.verticalHeader().setVisible(False)
        self.selection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.selection_table.cellClicked.connect(self.on_cell_clicked)
        layout.addWidget(self.selection_table)

        # 그래프 영역
        self.canvas = FigureCanvas(plt.Figure(figsize=(6, 4)))
        self.ax = self.canvas.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)   # 🔍 줌/팬/홈 버튼
        layout.addWidget(self.canvas)
        # 초기 빈 그래프
        self.ax.set_title("CAN DLC Graph")
        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel("값 (10진수)")
        self.ax.grid(True)
        self.canvas.draw()

    # -------------------------------
    # 외부에서 데이터 갱신 시 호출
    # -------------------------------
    def update_graph(self, df: pd.DataFrame, can_id: str):
        """새로운 DataFrame + 특정 CAN ID로 갱신"""
        if df.empty:
            return

        filtered = df[df["can_id"] == can_id].reset_index(drop=True)
        if filtered.empty:
            return

        self.df = filtered
        self.can_id = can_id
        self.dlc = int(self.df["dlc"].iloc[0])
        self.data_cols = [c for c in df.columns if str(c).isdigit()]

        # 라벨 갱신
        self.info_label.setText(f"CAN ID: {self.can_id} | DLC: {self.dlc}")

        # 테이블 갱신
        self.selection_table.setColumnCount(len(self.data_cols))
        self.selection_table.setHorizontalHeaderLabels([f"B{i}" for i in range(len(self.data_cols))])

        self.selected_bytes = []
        for j, col in enumerate(self.data_cols):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignCenter)
            if j >= self.dlc:  # DLC 초과는 회색 처리
                item.setFlags(Qt.NoItemFlags)
                item.setBackground(Qt.lightGray)
            self.selection_table.setItem(0, j, item)

        self.plot_graphs()

    # -------------------------------
    # UI 이벤트 핸들러
    # -------------------------------
    def on_cell_clicked(self, row, column):
        item = self.selection_table.item(row, column)
        if not item.flags() & Qt.ItemIsEnabled:
            return
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
        try:
            self.factor = float(self.factor_input.text())
        except Exception:
            self.factor = 1.0
        try:
            self.offset = float(self.offset_input.text())
        except Exception:
            self.offset = 0.0
        self.plot_graphs()

    # -------------------------------
    # 내부 계산 + 플로팅
    # -------------------------------
    def compute_decimal(self, row, byte_cols, endian="Big Endian"):
        bytes_list = []
        for c in byte_cols:
            try:
                b = row.get(c, 0)
                b_int = int(b, 16) if isinstance(b, str) else int(b)
            except Exception:
                b_int = 0
            bytes_list.append(b_int)

        if endian == "Little Endian":
            bytes_list = list(reversed(bytes_list))

        value = 0
        for b in bytes_list:
            value = (value << 8) | b
        return value

    def plot_graphs(self):
        self.ax.clear()

        if not self.selected_bytes or self.df.empty:
            self.ax.set_title("CAN DLC Graph")
            self.ax.set_xlabel("Timestamp")
            self.ax.set_ylabel("값 (10진수)")
            self.ax.grid(True)
            self.canvas.draw()
            return

        ts = self.df["timestamp"] if "timestamp" in self.df.columns else range(len(self.df))
        endian = self.endian_combo.currentText()

        try:
            y = self.df.apply(lambda row: self.compute_decimal(row, self.selected_bytes, endian), axis=1)
            y = y * self.factor + self.offset
            self.ax.plot(ts, y, label=f"CAN {self.can_id}", color="blue", linewidth=2)
        except Exception as e:
            print(f"[WARN] Plot error: {e}")

        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel("값 (10진수)")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()
