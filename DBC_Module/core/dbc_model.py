from typing import List
from core.signal import Signal

class DBCModel:
    def __init__(self):
        self.signals: List[Signal] = []
        self.file_path: str | None = None
        self.raw_text: str = ""

    def add_signal(self, sig: Signal):
        self.signals.append(sig)

    def load_from_list(self, sig_list: List[Signal]):
        self.signals = list(sig_list)
