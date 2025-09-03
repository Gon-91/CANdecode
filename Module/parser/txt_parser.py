from .base_parser import BaseCANParser
from ..message import CANMessage

class TXTParser(BaseCANParser):
    def __init__(self, file_path, field_order=None):
        """
        TXTParser

        Args:
            file_path (str): 읽을 파일 경로
            field_order (list, optional): 토큰별 필드 순서
            type_keyword (str, optional): 유효한 CAN 로그 라인을 식별하는 키워드
        """
        super().__init__(file_path)
        self.field_order = field_order or ["type","channel","timestamp","can_id","dlc","data","tid"]
        self.type_keyword = ["RX_MSG","TX_MSG"]
    def parse(self) -> list[CANMessage]:
        """
        파일 전체를 읽어서 CANMessage 리스트로 반환
        """
        messages = []
        with open(self.file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # -------------------------------
                # 1. 유효한 CAN 로그 라인인지 확인
                # 첫 토큰이 type_keyword와 일치해야 처리
                tokens = line.split()
                if not tokens or tokens[0] not in self.type_keyword:
                    continue  # 헤더나 엉뚱한 라인 무시
                # -------------------------------

                messages.append(self.parse_line(line))
        return messages

    def parse_line(self, line: str) -> CANMessage:
        """
        한 줄을 CANMessage 객체로 변환
        """
        # 1. 구분자 통일
        for sep in [",", ";", "\t"]:
            line = line.replace(sep, " ")

        # 2. 공백 토큰화
        tokens = [tok.split("=")[1] if "=" in tok else tok for tok in line.split() if tok]

        # 3. 필드 매핑
        values = {field: tokens[i] if i < len(tokens) else None for i, field in enumerate(self.field_order)}

        # 4. data를 DLC 기준으로 바이트 배열로 변환
        dlc = int(values.get("dlc")) if values.get("dlc") else 0
        data_str = values.get("data") or ""
        data_list = [data_str[i:i+2] for i in range(0, len(data_str), 2)][:dlc]


        return CANMessage(
            timestamp=float(values.get("timestamp")),
            can_id=values.get("can_id"),
            dlc=dlc,
            data=data_list,
            channel=values.get("channel"),
            type=values.get("type")
        )
