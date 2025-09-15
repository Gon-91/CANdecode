from .base_parser import BaseCANParser
from ..message import CANMessage
import pandas as pd
import can


class BLFParser(BaseCANParser):
    def __init__(self, file_path):
        """
        BLFParser

        Args:
            file_path (str): 읽을 BLF 파일 경로
        """
        super().__init__(file_path)

    def parse_df(self) -> pd.DataFrame:
        """
        BLF 전체를 읽어서 DataFrame 반환 (바이트별 컬럼 포함)
        """
        records = []
        with can.BLFReader(self.file_path) as reader:
            for msg in reader:
                if msg is None:
                    continue

                # DLC 기반 바이트 나누기
                dlc = msg.dlc
                data_list = [f"{b:02X}" for b in msg.data[:dlc]]

                record = {
                    "type": "RX_MSG" if not msg.is_rx else "TX_MSG",  # 필요시 수정
                    "channel": getattr(msg, "channel", None),
                    "timestamp": msg.timestamp,
                    "can_id": f"{msg.arbitration_id:04X}", #hex(msg.arbitration_id),
                    "dlc": dlc,
                }
                for i, byte in enumerate(data_list):
                    record[f"{i}"] = byte

                records.append(record)

        return pd.DataFrame(records)

    def parse_message(self) -> list[CANMessage]:
        """
        BLF 전체를 읽어서 CANMessage 리스트 반환
        """
        messages = []
        with can.BLFReader(self.file_path) as reader:
            for msg in reader:
                if msg is None:
                    continue

                dlc = msg.dlc
                data_list = [f"{b:02X}" for b in msg.data[:dlc]]

                messages.append(
                    CANMessage(
                        timestamp=msg.timestamp,
                        can_id=f"{msg.arbitration_id:04X}",#hex(msg.arbitration_id),
                        dlc=dlc,
                        data=data_list,
                        channel=getattr(msg, "channel", None),
                        type="RX_MSG" if not msg.is_rx else "TX_MSG",  # 필요시 조정
                    )
                )

        return messages
