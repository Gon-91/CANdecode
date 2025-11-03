from .base_parser import BaseCANParser
from ..message import CANMessage
import pandas as pd
import can
import binascii


class BLFParser(BaseCANParser):
    def __init__(self, file_path: str):
        """
        BLFParser

        Args:
            file_path (str): 읽을 BLF 파일 경로
        """
        super().__init__(file_path)

    def _iter_messages(self):
        """BLF 파일에서 메시지 generator 반환"""
        with can.BLFReader(self.file_path) as reader:
            for msg in reader:
                if msg is None:
                    continue
                yield msg

    def _msg_to_record(self, msg) -> dict:
        """can.Message → dict 변환 (DataFrame용)"""
        dlc = msg.dlc
        # 빠른 hex 변환
        hex_str = binascii.hexlify(msg.data[:dlc]).decode("ascii").upper()
        data_list = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]

        record = {
            "timestamp": msg.timestamp,
            "can_id": f"{msg.arbitration_id:04X}",
            "dlc": dlc,
            "channel": getattr(msg, "channel", None),
            "type": "RX_MSG" if not msg.is_rx else "TX_MSG",
        }
        # 바이트별 컬럼 추가
        for i, byte in enumerate(data_list):
            record[str(i)] = byte

        return record

    def _msg_to_canmessage(self, msg) -> CANMessage:
        """can.Message → CANMessage 변환"""
        dlc = msg.dlc
        data_list = [f"{b:02X}" for b in msg.data[:dlc]]
        return CANMessage(
            timestamp=msg.timestamp,
            can_id=f"{msg.arbitration_id:04X}",
            dlc=dlc,
            data=data_list,
            channel=getattr(msg, "channel", None),
            type="RX_MSG" if not msg.is_rx else "TX_MSG",
        )

    def parse_df(self) -> pd.DataFrame:
        """
        BLF 전체를 읽어서 DataFrame 반환 (바이트별 컬럼 포함)
        """
        records = [self._msg_to_record(msg) for msg in self._iter_messages()]
        return pd.DataFrame.from_records(records)

    def parse_message(self) -> list[CANMessage]:
        """
        BLF 전체를 읽어서 CANMessage 리스트 반환
        """
        return [self._msg_to_canmessage(msg) for msg in self._iter_messages()]
