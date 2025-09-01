import cantools
import re
from datetime import datetime


log_file = "Sample/Hyundai i20/Hyundai_i20_01_03_2021_CANcaseXL_Static.txt"

with open(log_file, 'r') as f:
    for line in f:
        if 'RX_MSG' in line:
            # 정규식으로 ID, DLC, Data 추출
            parts = [p.strip() for p in line.replace(',', '').split()]
            timestamp = int(parts[2].split('=')[1])
            can_id = int(parts[3].split('=')[1], 16)
            dlc = int(parts[4].split('=')[1])
            data = bytes.fromhex(parts[5])

print("FF")
