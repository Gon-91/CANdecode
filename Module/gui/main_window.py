from PyQt5.QtWidgets import QWidget, QHBoxLayout
from .file_list_widget import FileListWidget
from .table_view_widget import TableViewWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN 로그 뷰어")
        self.resize(1000, 600)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.file_list_widget = FileListWidget()
        self.table_view_widget = TableViewWidget()

        layout.addWidget(self.file_list_widget, 2)
        layout.addWidget(self.table_view_widget, 5)

        # 신호 연결
        self.file_list_widget.file_selected.connect(self.on_file_selected)

    def on_file_selected(self, file_path, df):
        self.table_view_widget.show_dataframe(df)
