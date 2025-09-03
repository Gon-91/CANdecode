from dataclasses import dataclass
from typing import Optional

@dataclass
class CANMessage:
    timestamp: Optional[float] = None
    can_id: Optional[str] = None
    dlc: Optional[int] = None
    data: Optional[str] = None
    channel: Optional[str] = None
    type: Optional[str] = None

