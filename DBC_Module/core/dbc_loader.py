import re
from core.message import Message
from core.signal import Signal

class DbcLoader:
    @staticmethod
    def load_dbc(path: str):
        messages = []
        current_msg = None
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        raw_text = "".join(lines)

        for line in lines:
            line = line.strip()
            if line.startswith("BO_"):
                m = re.match(r"BO_ (\d+)\s+(\w+)\s*:\s*(\d+)\s+\w+", line)
                if m:
                    msg_id = int(m.group(1))
                    name = m.group(2)
                    dlc = int(m.group(3))
                    current_msg = Message(name=name, msg_id=msg_id, dlc=dlc)
                    messages.append(current_msg)
            elif line.startswith("SG_") and current_msg:
                m = re.match(
                    r"SG_\s+(\w+)\s*:\s*(\d+)\|(\d+)@(\d)([+-])\s*"
                    r"\(([^,]+),([^)]+)\)\s*"
                    r"\[([^\|]+)\|([^\]]+)\]\s*"
                    r"\"([^\"]*)\"",
                    line
                )
                if m:
                    sig_name = m.group(1)
                    start_bit = int(m.group(2))
                    length = int(m.group(3))
                    byte_order = int(m.group(4))
                    value_type = m.group(5)
                    factor = float(m.group(6))
                    offset = float(m.group(7))
                    minimum = float(m.group(8))
                    maximum = float(m.group(9))
                    unit = m.group(10)
                    sig = Signal(
                        name=sig_name, start_bit=start_bit, length=length,
                        byte_order=byte_order, value_type=value_type,
                        factor=factor, offset=offset, minimum=minimum,
                        maximum=maximum, unit=unit
                    )
                    current_msg.add_signal(sig)
        return messages, raw_text

    @staticmethod
    def save_dbc(path, messages, raw_text):
        # 최소 구현: signal 변경 부분만 반영
        lines = raw_text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("SG_"):
                for msg in messages:
                    for sig in msg.signals:
                        if sig.name in line:
                            # 간단히 start|length@byte_order+...
                            new_line = f"SG_ {sig.name} : {sig.start_bit}|{sig.length}@{sig.byte_order}{sig.value_type} ({sig.factor},{sig.offset}) [0|0] \"{sig.unit}\" Vector__XXX"
                            lines[i] = new_line
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
