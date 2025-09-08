from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, QPushButton, QDialog, QCheckBox
)
from PyQt5.QtCore import QAbstractTableModel, Qt
import pandas as pd
from .dlc_graph_dialog import DlcGraphDialog


class PandasModel(QAbstractTableModel):
    """DataFrame을 QTableView에 표시하고 정렬을 지원하는 모델"""
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df.copy()

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
        colname = self._df.columns[column]
        ascending = order == Qt.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self._df = self._df.sort_values(by=colname, ascending=ascending).reset_index(drop=True)
        self.layoutChanged.emit()

    def update_dataframe(self, df: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()
        self._df = df.copy()
        self.layoutChanged.emit()


class TableViewWidget(QWidget):
    """DataFrame 뷰어 + CAN ID 필터링 + DLC 그래프 버튼"""
    def __init__(self):
        super().__init__()
        self._df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        self.model = None
        self.dlc_dialog = None  # 다이얼로그 참조
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("DataFrame 뷰어"))

        # CAN ID 필터 버튼
        btn_filter = QPushButton("CAN ID 필터")
        btn_filter.clicked.connect(self.open_can_id_filter)
        layout.addWidget(btn_filter)

        # DLC 그래프 버튼
        btn_graph = QPushButton("CAN DLC 그래프 보기")
        btn_graph.clicked.connect(self.open_dlc_graph_dialog)
        layout.addWidget(btn_graph)

        # 테이블 뷰
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        layout.addWidget(self.table_view)

    def show_dataframe(self, df: pd.DataFrame):
        self._df = df.copy()
        self.filtered_df = df.copy()
        self.model = PandasModel(self.filtered_df)
        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

    def open_can_id_filter(self):
        if self._df.empty:
            return
        dlg = CanIdFilterDialog(self._df["can_id"].unique(), self)
        if dlg.exec_():
            selected_ids = dlg.selected_ids
            if selected_ids:
                self.filtered_df = self._df[self._df["can_id"].isin(selected_ids)].reset_index(drop=True)
            else:
                self.filtered_df = self._df.copy()
            self.model.update_dataframe(self.filtered_df)

    def open_dlc_graph_dialog(self):
        """DLC 그래프 다이얼로그 열기 (비모달)"""
        if self.filtered_df.empty:
            return

        # 이미 열려있으면 재사용
        if self.dlc_dialog is None:
            self.dlc_dialog = DlcGraphDialog(self.filtered_df, parent=self)
        else:
            # DataFrame 갱신
            self.dlc_dialog.df = self.filtered_df.copy().reset_index(drop=True)
            self.dlc_dialog.plot_graphs()

        # 비모달로 보여주기
        self.dlc_dialog.show()
        self.dlc_dialog.raise_()
        self.dlc_dialog.activateWindow()


class CanIdFilterDialog(QDialog):
    """CAN ID 필터 다이얼로그"""
    def __init__(self, can_ids, parent=None):
        super().__init__(parent)
        self.resize(350, 750)

        self.setWindowTitle("CAN ID 필터")
        self.selected_ids = set()
        layout = QVBoxLayout()
        self.checkboxes = []

        for cid in sorted(set(can_ids)):
            cb = QCheckBox(str(cid))
            layout.addWidget(cb)
            self.checkboxes.append(cb)

        btn_apply = QPushButton("적용")
        btn_apply.clicked.connect(self.apply_filter)
        layout.addWidget(btn_apply)
        self.setLayout(layout)

    def apply_filter(self):
        self.selected_ids = {cb.text() for cb in self.checkboxes if cb.isChecked()}
        self.accept()
