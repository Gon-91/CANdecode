class DbcValidator:
    def __init__(self, db):
        self.db = db

    def check_duplicates(self):
        """중복 Frame ID, 신호명 확인"""
        issues = []
        seen_ids = set()
        for msg in self.db.messages:
            # Frame ID 중복 확인
            if msg.frame_id in seen_ids:
                issues.append(f"중복 Frame ID: {hex(msg.frame_id)}")
            seen_ids.add(msg.frame_id)

            # 신호명 중복 확인
            sig_names = [sig.name for sig in msg.signals]
            if len(sig_names) != len(set(sig_names)):
                issues.append(f"메시지 {msg.name}에 중복된 시그널명 존재")
        return issues
