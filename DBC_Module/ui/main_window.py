# main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox, QSplitter, QLabel
)
from PySide6.QtCore import Qt
from core.dbc_loader import DbcLoader
from autosave.autusaver import AutoSaver
from ui.bit_layout_view import BitTableView   
from ui.signal_table_view import SignalTableView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Editor Pro")
        self.messages = []
        self.raw_text = ""
        self.current_file = ""
        self.auto_save = False
        self.auto_save_manager = None

        # 중앙 위젯과 레이아웃
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        h_layout = QHBoxLayout(main_widget)

        # Splitter 사용: 좌-중-우 3단 구조
        splitter = QSplitter(Qt.Horizontal)
        h_layout.addWidget(splitter)

        # 좌측: 메시지 트리
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Messages")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        splitter.addWidget(self.tree)

        # 중앙: 시그널 테이블 + AutoSave/Open 버튼
        central_widget = QWidget()
        v_layout = QVBoxLayout(central_widget)

        self.signal_table = SignalTableView()
        self.signal_table.signal_changed_callback = self.on_signal_changed
        v_layout.addWidget(self.signal_table)

        # AutoSave 체크박스 + 상태 라벨
        self.auto_save_checkbox = QCheckBox("AutoSave")
        self.auto_save_checkbox.stateChanged.connect(self.toggle_auto_save)
        v_layout.addWidget(self.auto_save_checkbox)

        self.auto_save_status_label = QLabel("AutoSave: OFF")
        v_layout.addWidget(self.auto_save_status_label)

        # Open 버튼
        open_btn = QPushButton("Open DBC")
        open_btn.clicked.connect(self.open_file)
        v_layout.addWidget(open_btn)

        splitter.addWidget(central_widget)

        # 우측: 비트 레이아웃
        self.layout_view = BitTableView()
        self.layout_view.signal_changed_callback = self.on_signal_changed
        splitter.addWidget(self.layout_view)

        # 초기 비율 설정
        splitter.setSizes([200, 400, 600])

    # ----------------- AutoSave -----------------
    def toggle_auto_save(self, state):
        self.auto_save = state == Qt.Checked.value
        self.auto_save_status_label.setText(f"AutoSave: {'ON' if self.auto_save else 'OFF'}")
        if self.auto_save_manager:
            self.auto_save_manager.enabled = self.auto_save

    # ----------------- DBC 파일 열기 -----------------
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open DBC", "", "*.dbc")
        if not path:
            return
        self.current_file = path
        self.messages, self.raw_text = DbcLoader.load_dbc(path)
        self.refresh_tree()

        # AutoSaver 초기화
        self.auto_save_manager = AutoSaver(self.current_file, self.messages, self.raw_text)
        self.auto_save_manager.enabled = self.auto_save
        self.auto_save_status_label.setText(f"AutoSave: {'ON' if self.auto_save else 'OFF'}")

    # ----------------- 트리 갱신 -----------------
    def refresh_tree(self):
        self.tree.clear()
        for msg in self.messages:
            msg_item = QTreeWidgetItem([f"{msg.name} ({msg.id})"])
            msg_item.setData(0, 1, msg)
            for sig in msg.signals:
                sig_item = QTreeWidgetItem([sig.name])
                sig_item.setData(0, 1, sig)
                msg_item.addChild(sig_item)
            self.tree.addTopLevelItem(msg_item)

    # ----------------- 트리 클릭 이벤트 -----------------
    def on_tree_item_clicked(self, item, col):
        data = item.data(0, 1)
        if hasattr(data, "signals"):
            self.layout_view.set_message(data)
            self.signal_table.load_signals(data.signals)
        else:
            self.layout_view.set_selected_signal(data)

    # ----------------- 시그널 변경 콜백 -----------------
    def on_signal_changed(self, sig):
        """
        UI에서 Signal 변경 시 호출됨.
        SignalTableView / BitTableView 모두 동기화.
        """
        msg = self.layout_view.message
        if msg is None:
            return

        # 1) 메시지 내 signal 갱신
        for i, s in enumerate(msg.signals):
            if s.name == sig.name:
                msg.signals[i] = sig
                break

        # 2) MainWindow.messages 갱신
        for i, m in enumerate(self.messages):
            if m.name == msg.name:
                self.messages[i] = msg
                break

        # 3) BitTableView 갱신
        self.layout_view.set_message(msg)
        self.layout_view.set_selected_signal(sig)

        # 4) SignalTableView 갱신
        self.signal_table.load_signals(msg.signals)

        # 5) AutoSave
        if self.auto_save and self.auto_save_manager:
            print("AutoSave triggered: ", sig.name)
            self.auto_save_manager.signal_changed(sig)
