from .base_parser import BaseCANParser
from ..message import CANMessage

class CSVParser(BaseCANParser):
    def __init__(self, file_path, field_order=None):
        super().__init__(file_path)
        self.field_order = field_order or ["type","channel","timestamp","can_id","dlc","data","tid"]

    def parse(self) -> list[CANMessage]:
        messages = []
        with open(self.file_path, "r") as f:
            for line in f:
                if line.strip():
                    messages.append(self.parse_line(line.strip()))
        return messages
    def parse_line(self, line: str) -> CANMessage:
        for sep in [",", ";", "\t"]:
            line = line.replace(sep, " ")
        tokens = [tok.split("=")[1] if "=" in tok else tok for tok in line.split() if tok]
        values = {field: tokens[i] if i < len(tokens) else None for i, field in enumerate(self.field_order)}
        return CANMessage(
            timestamp=values.get("timestamp"),
            can_id=values.get("can_id"),
            dlc=values.get("dlc"),
            data=values.get("data"),
            channel=values.get("channel"),
            type_=values.get("type")
        )

