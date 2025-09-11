import cantools

class DbcLoader:
    def __init__(self):
        self.db = None
        self.filepath = None

    def load(self, filepath: str):
        """DBC 파일을 로드"""
        self.db = cantools.database.load_file(filepath)
        self.filepath = filepath
        return self.db

    def save(self, filepath: str = None):
        """DBC를 파일로 저장"""
        if filepath is None:
            filepath = self.filepath
        if not self.db:
            raise ValueError("DBC가 로드되지 않았습니다.")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.db.as_dbc_string())
