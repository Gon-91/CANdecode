class Message:
    def __init__(self, name, msg_id, dlc):
        self.name = name
        self.id = msg_id
        self.dlc = dlc
        self.signals = []

    def add_signal(self, sig):
        self.signals.append(sig)
