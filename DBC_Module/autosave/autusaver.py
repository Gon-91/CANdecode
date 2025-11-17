import time
import threading
from core.dbc_loader import DbcLoader

class AutoSaver:
    def __init__(self, model, interval_sec: float = 2.0):
        self.model = model
        self.interval = float(interval_sec)
        self.enabled = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while True:
            time.sleep(self.interval)
            if not self.enabled:
                continue
            if not getattr(self.model, "file_path", None):
                continue
            try:
                DbcLoader.save_json(self.model.file_path, self.model.signals)
            except Exception as e:
                # autosave should not crash the app; print for debug
                print("AutoSave error:", e)
