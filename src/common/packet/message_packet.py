from src.common.config import ENCODING
from .packet import Packet
from .packet_types import PacketType


class MessagePacket(Packet):
    def __init__(self, message: str, sender: str = None) -> None:
        super().__init__(PacketType.MESSAGE)

        self.append_var_len(bytes(message, encoding=ENCODING))
        if sender is not None:
            self.append_var_len(bytes(sender, encoding=ENCODING))
