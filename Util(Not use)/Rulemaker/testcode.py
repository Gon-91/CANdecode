import re

def build_pattern(sample_line, mapping):
    pattern = re.escape(sample_line)
    used_fields = set()

    for field, value in mapping.items():
        if value in sample_line:
            if field not in used_fields:
                # 숫자/HEX/일반 문자열 구분
                if re.fullmatch(r"[0-9A-Fa-f]+", value):
                    regex_piece = f"(?P<{field}>[0-9A-Fa-f]+)"
                elif re.fullmatch(r"\d+", value):
                    regex_piece = f"(?P<{field}>\\d+)"
                else:
                    regex_piece = f"(?P<{field}>.+?)"
                # 첫 번째만 그룹화
                pattern = pattern.replace(re.escape(value), regex_piece, 1)
                used_fields.add(field)
            else:
                # 두 번째 이상은 그냥 매칭
                pattern = pattern.replace(re.escape(value), ".+?", 1)

    return pattern
def build_pattern2(sample_line, mapping):
    tokens = sample_line.split()
    pattern_parts = []
    used_fields = set()

    for token in tokens:
        field = None
        for k, v in mapping.items():
            if token == v and k not in used_fields:
                field = k
                used_fields.add(k)
                break

        if field:
            # 숫자 / HEX / 일반 문자열 구분
            if re.fullmatch(r"[0-9A-Fa-f]+", token):
                regex_piece = f"(?P<{field}>[0-9A-Fa-f]+)"
            elif token.isdigit():
                regex_piece = f"(?P<{field}>\\d+)"
            else:
                regex_piece = f"(?P<{field}>\\S+)"
        else:
            # 고정값 대신 동적 매칭
            if token.isdigit():
                regex_piece = r"\d+"
            else:
                regex_piece = r"\S+"

        pattern_parts.append(regex_piece)

    return r"\s+".join(pattern_parts)


# ---------------- 테스트 ----------------
sample = "RX_MSG c=0, t=6217728, id=0386 l=8, 00C0000000400080 tid=00"
mapping = {
    "type" : "RX_MSG",
    "timestamp": "6217728",
    "can_id": "0386",
    "dlc": "8",
    "data": "00C0000000400080"
}

pattern = build_pattern2(sample, mapping)
print("Generated regex:\n", pattern)

regex = re.compile(pattern)
match = regex.match(sample)
print("Result dict:", match.groupdict())

sample2 = "TX_MSG c=0, t=10240000, id=0386 l=4, 00C001C000400080 tid=00"
pattern2 =  "(?P<type>.+?)\ c=0,\ t=(?P<timestamp>[0-9A-Fa-f]+),\ id=(?P<can_id>[0-9A-Fa-f]+)\ l=(?P<dlc>[0-9A-Fa-f]+),\ (?P<data>[0-9A-Fa-f]+)\ tid=00"
regex = re.compile(pattern2)
match = regex.match(sample2)
print("Result dict:", match.groupdict())




print("-"*50)

# ---------------- 테스트 ----------------
sample = "RX_MSG 0 6217728 0386 8 00C0000000400080 00"
mapping = {
    "type" : "RX_MSG",
    "timestamp": "6217728",
    "can_id": "0386",
    "dlc": "8",
    "data": "00C0000000400080"
}

pattern = build_pattern2(sample, mapping)
print("Generated regex:\n", pattern)

regex = re.compile(pattern)
match = regex.match(sample)
print("Result dict:", match.groupdict())

sample2 = "RX_MSG 2 6217728 0386 2 00C0000000400080 00"
pattern2 =  "(?P<type>.+?)\ 0\ (?P<timestamp>[0-9A-Fa-f]+)\ (?P<can_id>[0-9A-Fa-f]+)\ (?P<dlc>[0-9A-Fa-f]+)\ (?P<data>[0-9A-Fa-f]+)\ 00"
regex = re.compile(pattern2)
match = regex.match(sample2)
print("Result dict:", match.groupdict())