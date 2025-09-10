from PyQt5.QtWidgets import QWidget, QHBoxLayout
from .file_list_widget import FileListWidget
from .table_view_widget import TableViewWidget
from .dlc_graph_widget import DlcGraphWidget
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN 로그 뷰어")
        self.resize(1400, 800)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.file_list_widget = FileListWidget()
        self.table_view_widget = TableViewWidget()
        self.dlc_graph_widget = DlcGraphWidget()
        layout.addWidget(self.file_list_widget, 2)
        layout.addWidget(self.table_view_widget, 5)
        layout.addWidget(self.dlc_graph_widget, 3)   # 비율 3
        # 신호 연결
        self.file_list_widget.file_selected.connect(self.on_file_selected)

        
        self.table_view_widget.can_id_selected.connect(
            lambda can_id: self.dlc_graph_widget.update_graph(
                self.table_view_widget.filtered_df, can_id
            )
        )
    def on_file_selected(self, file_path, df):
        # 테이블 갱신
        self.table_view_widget.show_dataframe(df)

        # ✅ 자동으로 첫 번째 CAN_ID 기준 그래프 갱신
        if not df.empty and "can_id" in df.columns:
            can_id = df["can_id"].iloc[0]
            self.dlc_graph_widget.update_graph(df, can_id)