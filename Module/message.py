class CANMessage:
    def __init__(self, type_="RX_MSG",timestamp=None, can_id=None, dlc=None, data=None, channel=None, is_fd=False ):
        self.type = type_
        self.is_fd = is_fd
        self.timestamp = timestamp
        self.can_id = can_id
        self.dlc = dlc
        self.data = data
        self.channel = channel

