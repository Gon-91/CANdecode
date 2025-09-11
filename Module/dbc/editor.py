import cantools

class DbcEditor:
    def __init__(self, db):
        self.db = db

    def add_signal(self, msg_name: str, signal_name: str, start_bit: int,
                   length: int, factor: float, offset: float, unit: str = ""):
        """DBC 메시지에 새 신호 추가"""
        msg = self.db.get_message_by_name(msg_name)
        new_signal = cantools.db.Signal(
            name=signal_name,
            start=start_bit,
            length=length,
            is_signed=False,
            factor=factor,
            offset=offset,
            unit=unit
        )
        msg.signals.append(new_signal)

    def modify_signal(self, msg_name: str, signal_name: str, factor: float, offset: float):
        """기존 신호의 factor/offset 수정"""
        msg = self.db.get_message_by_name(msg_name)
        for sig in msg.signals:
            if sig.name == signal_name:
                sig.factor = factor
                sig.offset = offset
                return True
        return False
