from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QAction
from .file_list_widget import FileListWidget
from .table_view_widget import TableViewWidget
from .dlc_graph_widget import DlcGraphWidget
from .dbc_dialog import DBCManagerDialog   # ✅ DBC 다이얼로그 불러오기
from ..manager.dbcmanager import DBCManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN 로그 뷰어")
        self.resize(1400, 800)

        self.dbc_manager = DBCManager()  # ✅ 나중에 manager/dbcmanager.py 객체 연결
        self.init_ui()

    def init_ui(self):
        # 중앙 위젯 (기존 QWidget 기반 UI를 QMainWindow에 넣음)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # 🔹 위젯 구성
        self.file_list_widget = FileListWidget()
        self.table_view_widget = TableViewWidget()
        self.dlc_graph_widget = DlcGraphWidget()

        layout.addWidget(self.file_list_widget, 2)
        layout.addWidget(self.table_view_widget, 5)
        layout.addWidget(self.dlc_graph_widget, 3)

        # 신호 연결
        self.file_list_widget.file_selected.connect(self.on_file_selected)
        self.table_view_widget.can_id_selected.connect(
            lambda can_id: self.dlc_graph_widget.update_graph(
                self.table_view_widget.filtered_df, can_id
            )
        )

        # 🔹 메뉴바 설정
        menubar = self.menuBar()

        # [파일] 메뉴
        file_menu = menubar.addMenu("파일")

        # [도구] 메뉴
        tools_menu = menubar.addMenu("도구")

        # 도구 → DBC Manager 열기
        dbc_action = QAction("DBC Manager 열기", self)
        dbc_action.triggered.connect(self.open_dbc_manager)
        tools_menu.addAction(dbc_action)

        # [도움말] 메뉴
        help_menu = menubar.addMenu("도움말")

    def on_file_selected(self, file_path, df):
        self.table_view_widget.show_dataframe(df)

        if not df.empty and "can_id" in df.columns:
            can_id = df["can_id"].iloc[0]
            self.dlc_graph_widget.update_graph(df, can_id)

    def open_dbc_manager(self):
        """DBC Manager 다이얼로그 열기"""
        df = self.table_view_widget._df
        dlg = DBCManagerDialog(self.dbc_manager, df, self)
        dlg.exec_()
