from dbc.loader import DbcLoader
from dbc.decoder import DbcDecoder
from dbc.editor import DbcEditor
from dbc.validator import DbcValidator

class DBCManager:
    """UI에서 직접 사용하는 통합 클래스"""
    def __init__(self):
        self.loader = DbcLoader()
        self.db = None

    def load_dbc(self, filepath: str):
        self.db = self.loader.load(filepath)
        self.decoder = DbcDecoder(self.db)
        self.editor = DbcEditor(self.db)
        self.validator = DbcValidator(self.db)
        return self.db

    def save_dbc(self, filepath: str = None):
        self.loader.save(filepath)

    def decode_dataframe(self, df):
        return self.decoder.decode_dataframe(df)

    def add_signal(self, *args, **kwargs):
        return self.editor.add_signal(*args, **kwargs)

    def modify_signal(self, *args, **kwargs):
        return self.editor.modify_signal(*args, **kwargs)

    def validate(self):
        return self.validator.check_duplicates()
