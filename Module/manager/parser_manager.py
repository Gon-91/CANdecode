from ..parser.txt_parser import TXTParser
from ..parser.csv_parser import CSVParser  # 추후 추가
from pathlib import Path
def get_parser(file_path, **kwargs):

    file_path = Path(file_path)
    ext = file_path.suffix.lower()  # .txt, .csv 등

    if ext == ".txt":
        return TXTParser(file_path, **kwargs)
    elif ext == ".csv":
        return CSVParser(file_path, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
