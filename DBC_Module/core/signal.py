from PySide6.QtGui import QColor
import random

class Signal:
    def __init__(self, name, start_bit, length, byte_order=1, value_type='+', factor=1.0, offset=0.0, minimum=0, maximum=255, unit=''):
        self.name = name
        self.start_bit = start_bit
        self.length = length
        self.byte_order = byte_order  # 0=Motorola, 1=Intel
        self.value_type = value_type
        self.factor = factor
        self.offset = offset
        self.minimum = minimum
        self.maximum = maximum
        self.unit = unit
        self.color = QColor(*[random.randint(50, 255) for _ in range(3)])
