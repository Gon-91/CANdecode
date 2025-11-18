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
            # 메시지(BO_) 라인
            if line.startswith("BO_"):
                m = re.match(r"BO_ (\d+)\s+(\w+)\s*:\s*(\d+)\s+\w+", line)
                if m:
                    msg_id = int(m.group(1))
                    name = m.group(2)
                    dlc = int(m.group(3))
                    current_msg = Message(name=name, msg_id=msg_id, dlc=dlc)
                    messages.append(current_msg)

            # 시그널(SG_) 라인
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
                        name=sig_name,
                        start_bit=start_bit,
                        length=length,
                        byte_order=byte_order,
                        value_type=value_type,
                        factor=factor,
                        offset=offset,
                        minimum=minimum,
                        maximum=maximum,
                        unit=unit
                    )
                    current_msg.add_signal(sig)
        return messages, raw_text

    @staticmethod
    def save_dbc(path, messages, raw_text):
        """
        원본 raw_text 흐름을 유지하며 SG_ 라인의 start_bit, length 등을 정확하게 치환.
        """
        lines = raw_text.splitlines()

        # SG_ 라인의 정규식
        sig_pattern = re.compile(
            r'^(\s*SG_\s+)(\w+)(\s*:\s*)(\d+)\|(\d+)@(\d)([+-])(.*)$'
        )
        # 그룹 구조:
        # 1: 앞공백+SG_
        # 2: 시그널 이름
        # 3: ' : '
        # 4: start_bit
        # 5: length
        # 6: byte_order
        # 7: signed(+/-)
        # 8: 나머지 (scaling 등)

        # message 구조를 검색하기 쉽게 dictionary로 구성
        signal_map = {}
        for msg in messages:
            for sig in msg.signals:
                signal_map[sig.name] = sig

        new_lines = []

        for line in lines:
            m = sig_pattern.match(line)
            if m:
                sig_name = m.group(2)

                if sig_name in signal_map:
                    sig = signal_map[sig_name]

                    # 새로운 SG_ 라인 구성
                    new_line = (
                        f"{m.group(1)}{sig.name}"
                        f"{m.group(3)}{sig.start_bit}|{sig.length}"
                        f"@{sig.byte_order}{sig.value_type}"
                        f"{m.group(8)}"
                    )

                    new_lines.append(new_line)
                    continue

            # SG_ 라인이 아니면 그냥 저장
            new_lines.append(line)

        # 파일로 저장
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
