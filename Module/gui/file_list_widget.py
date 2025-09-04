from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog
from PyQt5.QtCore import pyqtSignal

from ..manager.parser_manager import get_parser
from ..utils.dataframe import messages_to_dataframe


class FileListWidget(QWidget):
    file_selected = pyqtSignal(str, object)  # file_path, DataFrame

    def __init__(self):
        super().__init__()
        self.df_dict = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("선택된 파일 목록"))
        self.list_widget = QListWidget()
        self.list_widget.clicked.connect(self.on_file_selected)
        layout.addWidget(self.list_widget)

        self.btn_add_file = QPushButton("파일 추가")
        self.btn_add_file.clicked.connect(self.add_file)
        layout.addWidget(self.btn_add_file)

    def add_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "CAN 로그 파일 선택", "", "Text Files (*.txt)")
        for file_path in files:
            if file_path not in self.df_dict:
                self.list_widget.addItem(file_path)
                parser = get_parser( file_path)
                df = parser.parse_df()
                self.df_dict[file_path] = df

    def on_file_selected(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        file_path = items[0].text()
        df = self.df_dict.get(file_path)
        if df is not None:
            self.file_selected.emit(file_path, df)
