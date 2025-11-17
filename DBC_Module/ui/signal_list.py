from PySide6.QtWidgets import QListWidget, QListWidgetItem

class SignalList(QListWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def refresh(self):
        self.clear()
        for sig in self.model.signals:
            self.addItem(QListWidgetItem(sig.name))
