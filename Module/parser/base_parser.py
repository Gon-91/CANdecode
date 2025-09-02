class BaseCANParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self) -> list:
        raise NotImplementedError
