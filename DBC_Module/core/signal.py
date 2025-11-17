from PySide6.QtGui import QColor

class Signal:
    def __init__(self, name, start_bit, length, byte_order=1, value_type="+",
                 factor=1.0, offset=0.0, minimum=0.0, maximum=0.0, unit="", color=None):
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
        self.color = color or QColor(180, 255, 180)
