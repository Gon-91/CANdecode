from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import pandas as pd

class TableViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("DataFrame 뷰어"))
        self.table_view = QTableView()
        layout.addWidget(self.table_view)

    def show_dataframe(self, df: pd.DataFrame):
        model = QStandardItemModel()
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(df.columns.tolist())

        for row in df.itertuples(index=False):
            items = [QStandardItem(str(field)) for field in row]
            model.appendRow(items)

        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()
