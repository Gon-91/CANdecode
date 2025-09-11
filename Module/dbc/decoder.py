import pandas as pd

class DbcDecoder:
    def __init__(self, db):
        self.db = db

    def decode_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrame의 'can_id' + 'data' 컬럼을 이용해 신호 해석
        data는 bytes 또는 list[int] 형식이어야 함
        """
        if "can_id" not in df.columns or "data" not in df.columns:
            raise ValueError("DataFrame must have 'can_id' and 'data' columns")

        decoded_rows = []
        for _, row in df.iterrows():
            try:
                can_id = row["can_id"]
                if isinstance(can_id, str):
                    can_id = int(can_id, 16)
                msg = self.db.get_message_by_frame_id(can_id)

                payload = row["data"]
                if isinstance(payload, list):
                    payload = bytes(payload)

                decoded = msg.decode(payload)
                decoded_rows.append(decoded)
            except Exception:
                decoded_rows.append({})
        decoded_df = pd.DataFrame(decoded_rows)
        return pd.concat([df.reset_index(drop=True), decoded_df], axis=1)
