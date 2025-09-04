from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt
import pandas as pd

class PandasModel(QAbstractTableModel):
    """Pandas DataFrame을 QTableView에 표시하기 위한 모델"""
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            val = self._df.iat[index.row(), index.column()]
            # NaN 처리
            if pd.isna(val):
                return ""
            return str(val)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section])
        else:
            return str(section)

class TableViewWidget(QWidget):
    """DataFrame 뷰어 위젯"""
    def __init__(self):
        super().__init__()
        self._df = pd.DataFrame()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("DataFrame 뷰어"))
        self.table_view = QTableView()
        layout.addWidget(self.table_view)

    def show_dataframe(self, df: pd.DataFrame):
        """DataFrame을 테이블에 표시"""
        self._df = df
        model = PandasModel(df)
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()