from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QColorDialog
from PySide6.QtCore import Qt

class SignalTableView(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(11)
        self.setHorizontalHeaderLabels(
            ["Name","StartBit","Length","ByteOrder","Type","Factor","Offset","Min","Max","Unit","Color"]
        )
        self.signals=[]
        self.signal_changed_callback=None
        self.cellChanged.connect(self.on_cell_changed)

    def load_signals(self, signals):
        self.blockSignals(True)
        self.signals=signals
        self.setRowCount(len(signals))
        for row,sig in enumerate(signals):
            self.setItem(row,0,QTableWidgetItem(sig.name))
            self.setItem(row,1,QTableWidgetItem(str(sig.start_bit)))
            self.setItem(row,2,QTableWidgetItem(str(sig.length)))

            cb_order=QComboBox()
            cb_order.addItems(["Motorola","Intel"])
            cb_order.setCurrentIndex(sig.byte_order)
            cb_order.currentIndexChanged.connect(lambda idx,s=sig:self.on_order_changed(s,idx))
            self.setCellWidget(row,3,cb_order)

            cb_type=QComboBox()
            cb_type.addItems(["+","-"])
            cb_type.setCurrentText(sig.value_type)
            cb_type.currentIndexChanged.connect(lambda idx,s=sig:self.on_type_changed(s,idx))
            self.setCellWidget(row,4,cb_type)

            self.setItem(row,5,QTableWidgetItem(str(sig.factor)))
            self.setItem(row,6,QTableWidgetItem(str(sig.offset)))
            self.setItem(row,7,QTableWidgetItem(str(sig.minimum)))
            self.setItem(row,8,QTableWidgetItem(str(sig.maximum)))
            self.setItem(row,9,QTableWidgetItem(sig.unit))

            # Color selector
            btn=QPushButton()
            btn.setStyleSheet(f"background-color:{sig.color.name()}")
            btn.clicked.connect(lambda checked,s=sig,b=btn:self.choose_color(s,b))
            self.setCellWidget(row,10,btn)
        self.blockSignals(False)

    def choose_color(self,sig,btn):
        color=QColorDialog.getColor(sig.color,self)
        if color.isValid():
            sig.color=color
            btn.setStyleSheet(f"background-color:{color.name()}")
            if self.signal_changed_callback: self.signal_changed_callback(sig)

    def on_order_changed(self,sig,idx):
        sig.byte_order=idx
        if self.signal_changed_callback: self.signal_changed_callback(sig)

    def on_type_changed(self,sig,idx):
        sig.value_type="+" if idx==0 else "-"
        if self.signal_changed_callback: self.signal_changed_callback(sig)

    def on_cell_changed(self,row,col):
        sig=self.signals[row]
        if col==0: sig.name=self.item(row,col).text()
        elif col==1: sig.start_bit=int(self.item(row,col).text())
        elif col==2: sig.length=int(self.item(row,col).text())
        elif col==5: sig.factor=float(self.item(row,col).text())
        elif col==6: sig.offset=float(self.item(row,col).text())
        elif col==7: sig.minimum=float(self.item(row,col).text())
        elif col==8: sig.maximum=float(self.item(row,col).text())
        elif col==9: sig.unit=self.item(row,col).text()
        if self.signal_changed_callback: self.signal_changed_callback(sig)
