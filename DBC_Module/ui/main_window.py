from PySide6.QtWidgets import QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox
from core.dbc_loader import DbcLoader
from ui.bit_layout_view import BitLayoutView
from ui.signal_table_view import SignalTableView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Editor Pro")
        self.messages=[]
        self.raw_text=""
        self.current_file=""
        self.auto_save=False

        main_widget=QWidget()
        self.setCentralWidget(main_widget)
        h_layout=QHBoxLayout(main_widget)

        self.tree=QTreeWidget()
        self.tree.setHeaderLabel("Messages")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        h_layout.addWidget(self.tree,1)

        self.layout_view=BitLayoutView()
        self.layout_view.signal_changed_callback=self.on_signal_changed
        h_layout.addWidget(self.layout_view,2)

        v_right=QVBoxLayout()
        self.signal_table=SignalTableView()
        self.signal_table.signal_changed_callback=self.on_signal_changed
        v_right.addWidget(self.signal_table)
        self.auto_save_checkbox=QCheckBox("AutoSave")
        self.auto_save_checkbox.stateChanged.connect(self.toggle_auto_save)
        v_right.addWidget(self.auto_save_checkbox)
        open_btn=QPushButton("Open DBC")
        open_btn.clicked.connect(self.open_file)
        v_right.addWidget(open_btn)
        h_layout.addLayout(v_right,2)

    def toggle_auto_save(self,state):
        self.auto_save=state==2

    def open_file(self):
        path,_=QFileDialog.getOpenFileName(self,"Open DBC","","*.dbc")
        if not path: return
        self.current_file=path
        self.messages,self.raw_text=DbcLoader.load_dbc(path)
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.clear()
        for msg in self.messages:
            msg_item=QTreeWidgetItem([f"{msg.name} ({msg.id})"])
            msg_item.setData(0,1,msg)
            for sig in msg.signals:
                sig_item=QTreeWidgetItem([sig.name])
                sig_item.setData(0,1,sig)
                msg_item.addChild(sig_item)
            self.tree.addTopLevelItem(msg_item)

    def on_tree_item_clicked(self,item,col):
        data=item.data(0,1)
        if hasattr(data,"signals"):
            self.layout_view.set_message(data)
            self.signal_table.load_signals(data.signals)
        else:
            self.layout_view.set_selected_signal(data)

    def on_signal_changed(self,sig):
        self.signal_table.load_signals(self.layout_view.message.signals)
        self.layout_view.update()
        if self.auto_save:
            DbcLoader.save_dbc(self.current_file,self.messages,self.raw_text)
