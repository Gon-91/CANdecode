import pandas as pd
from ..message import CANMessage

def messages_to_dataframe(messages: list[CANMessage]) -> pd.DataFrame:
    """
    CANMessage 리스트를 DataFrame으로 변환.
    - data는 DLC 기준으로 분리하여 바이트 컬럼 추가
    """
    records = []
    for msg in messages:
        record = {
            "timestamp": msg.timestamp,
            "can_id": msg.can_id,
            "dlc": msg.dlc,
            "channel": msg.channel,
            "type": msg.type
        }
        # data를 바이트 단위로 분리
        for i, byte in enumerate(msg.data or []):
            record[f"{i}"] = byte
        records.append(record)
    return pd.DataFrame(records)


def sort_by_column(df : pd.DataFrame , column: str, ascending: bool = True  ) -> pd.DataFrame :
    return df.sort_values(by=column, ascending=ascending)

def filter_by_can_id(df: pd.DataFrame, can_id: str) -> pd.DataFrame:
    """
    특정 CAN ID만 필터링
    """
    return df[df["can_id"] == can_id]
def filter_by_timestamp_range(df: pd.DataFrame, start: float, end: float) -> pd.DataFrame:
    """
    timestamp 범위로 필터링
    """
    return df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]
def select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    원하는 컬럼만 선택
    """
    return df[columns].copy()