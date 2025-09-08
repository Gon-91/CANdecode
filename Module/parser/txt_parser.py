from .base_parser import BaseCANParser
from ..message import CANMessage
import pandas as pd
import re


class TXTParser(BaseCANParser):
    def __init__(self, file_path, field_order=None):
        """
        TXTParser

        Args:
            file_path (str): 읽을 파일 경로
            field_order (list, optional): 토큰별 필드 순서
            type_keyword (list[str], optional): 유효한 CAN 로그 라인을 식별하는 키워드
        """
        super().__init__(file_path)
        self.field_order = field_order or ["type","channel","timestamp","can_id","dlc","data","tid"]
        self.type_keyword = ["RX_MSG","TX_MSG"]

    def parse_df(self) -> pd.DataFrame:
        """
        파일 전체를 읽어서 DataFrame 반환 (바이트별 컬럼 포함)
        """
        records = []
        with open(self.file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 첫 토큰이 type_keyword 와 일치하는 경우만 처리
                tokens = line.split()
                if not tokens or tokens[0] not in self.type_keyword:
                    continue

                record = self._parse_line_common(line)
                if record:
                    records.append(record)

        return pd.DataFrame(records)

    def parse_message(self) -> list[CANMessage]:
        """
        파일 전체를 읽어서 CANMessage 리스트 반환
        """
        messages = []
        with open(self.file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                tokens = line.split()
                if not tokens or tokens[0] not in self.type_keyword:
                    continue

                msg = self._parse_line_message(line)
                if msg:
                    messages.append(msg)

        return messages

    def _parse_line_common(self, line: str) -> dict:
        """
        한 줄을 dict로 변환 (DataFrame용, 바이트별 컬럼 포함)
        """
        # 1. 구분자 통일 + 토큰화
        tokens = re.split(r"[,\t; ]+", line.strip())
        tokens = [tok.split("=")[1] if "=" in tok else tok for tok in tokens if tok]

        # 2. 필드 매핑
        values = {field: tokens[i] if i < len(tokens) else None
                  for i, field in enumerate(self.field_order)}

        # 3. 타입 변환 + DLC 기반 데이터 분리
        try:
            timestamp = float(values.get("timestamp") or 0.0) / 1000000
        except ValueError:
            timestamp = 0.0

        try:
            dlc = int(values.get("dlc") or 0)
        except ValueError:
            dlc = 0

        # 4. data → 바이트 분리
        data_str = values.get("data") or ""
        data_list = [data_str[i:i+2] for i in range(0, len(data_str), 2)][:dlc]

        record = {
            "type": values.get("type"),
            "channel": values.get("channel"),
            "timestamp": timestamp,
            "can_id": values.get("can_id"),
            "dlc": dlc,
        }
        for i, byte in enumerate(data_list):
            record[f"{i}"] = byte

        return record

    def _parse_line_message(self, line: str) -> CANMessage:
        """
        한 줄을 CANMessage 객체로 변환
        """
        for sep in [",", ";", "\t"]:
            line = line.replace(sep, " ")

        tokens = [tok.split("=")[1] if "=" in tok else tok for tok in line.split() if tok]
        values = {field: tokens[i] if i < len(tokens) else None
                  for i, field in enumerate(self.field_order)}

        dlc = int(values.get("dlc")) if values.get("dlc") else 0
        data_str = values.get("data") or ""
        data_list = [data_str[i:i+2] for i in range(0, len(data_str), 2)][:dlc]

        return CANMessage(
            timestamp=float(values.get("timestamp") or 0.0),
            can_id=values.get("can_id"),
            dlc=dlc,
            data=data_list,
            channel=values.get("channel"),
            type=values.get("type")
        )