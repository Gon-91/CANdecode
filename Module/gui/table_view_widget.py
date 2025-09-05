from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView,
    QPushButton, QDialog, QCheckBox
)
from PyQt5.QtCore import QAbstractTableModel, Qt
import pandas as pd


class PandasModel(QAbstractTableModel):
    """DataFrame을 QTableView에 표시하고 정렬을 지원하는 모델"""
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df.copy()  # 내부 데이터 복사

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            val = self._df.iat[index.row(), index.column()]
            return "" if pd.isna(val) else str(val)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section])
        else:
            return str(section)

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder):
        """헤더 클릭 시 DataFrame 자체를 정렬"""
        colname = self._df.columns[column]
        ascending = order == Qt.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self._df = self._df.sort_values(by=colname, ascending=ascending).reset_index(drop=True)
        self.layoutChanged.emit()

    def update_dataframe(self, df: pd.DataFrame):
        """DataFrame 갱신"""
        self.layoutAboutToBeChanged.emit()
        self._df = df.copy()
        self.layoutChanged.emit()


class TableViewWidget(QWidget):
    """DataFrame 뷰어 + CAN ID 필터링"""
    def __init__(self):
        super().__init__()
        self._df = pd.DataFrame()  # 원본 DataFrame
        self.filtered_df = pd.DataFrame()  # 필터 적용 후 DataFrame
        self.model = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("DataFrame 뷰어"))

        # CAN ID 필터 버튼
        btn_filter = QPushButton("CAN ID 필터")
        btn_filter.clicked.connect(self.open_can_id_filter)
        layout.addWidget(btn_filter)

        # 테이블 뷰
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)  # 헤더 클릭 정렬
        layout.addWidget(self.table_view)

    def show_dataframe(self, df: pd.DataFrame):
        """DataFrame 표시 (원본 + 필터 적용)"""
        self._df = df.copy()
        self.filtered_df = df.copy()
        self.model = PandasModel(self.filtered_df)
        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

    def open_can_id_filter(self):
        """CAN ID 필터 다이얼로그 열기"""
        if self._df.empty:
            return
        dlg = CanIdFilterDialog(self._df["can_id"].unique(), self)
        if dlg.exec_():
            selected_ids = dlg.selected_ids
            if selected_ids:
                # 선택된 CAN ID만 필터링
                self.filtered_df = self._df[self._df["can_id"].isin(selected_ids)].reset_index(drop=True)
            else:
                # 필터 해제
                self.filtered_df = self._df.copy()
            # 모델 갱신
            self.model.update_dataframe(self.filtered_df)


class CanIdFilterDialog(QDialog):
    """CAN ID 필터 다이얼로그 (체크박스 목록)"""
    def __init__(self, can_ids, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CAN ID 필터")
        self.selected_ids = set()
        layout = QVBoxLayout()
        self.checkboxes = []

        # CAN ID 체크박스 생성
        for cid in sorted(set(can_ids)):
            cb = QCheckBox(str(cid))
            layout.addWidget(cb)
            self.checkboxes.append(cb)

        # 적용 버튼
        apply_btn = QPushButton("적용")
        apply_btn.clicked.connect(self.apply_filter)
        layout.addWidget(apply_btn)
        self.setLayout(layout)

    def apply_filter(self):
        """선택된 ID 수집 후 다이얼로그 종료"""
        self.selected_ids = {cb.text() for cb in self.checkboxes if cb.isChecked()}
        self.accept()
