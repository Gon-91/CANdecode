# autosave/autusaver.py
import os
from core.dbc_loader import DbcLoader

class AutoSaver:
    """
    시그널 변경 시 자동으로 DBC 파일을 저장하는 클래스
    MainWindow에서 on_signal_changed 콜백과 연동
    """
    def __init__(self, file_path: str, messages: list, raw_text: str):
        self.file_path = file_path
        self.messages = messages
        self.raw_text = raw_text
        self.enabled = True

    def signal_changed(self, sig):
        """
        시그널 변경 시 호출.
        실제 파일 저장 수행.
        """
        if not self.enabled or not self.file_path:
            return
        # messages와 raw_text를 이용하여 DBC 저장
        DbcLoader.save_dbc(self.file_path, self.messages, self.raw_text)
