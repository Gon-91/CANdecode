from ..parser.txt_parser import TXTParser
from ..parser.csv_parser import CSVParser  # 추후 추가

def get_parser(file_path, file_type, **kwargs):
    if file_type.lower() == "txt":
        return TXTParser(file_path, **kwargs)
    elif file_type.lower() == "csv":
        return CSVParser(file_path, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
