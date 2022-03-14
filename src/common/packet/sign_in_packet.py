from src.common.config import ENCODING
from src.common.status_codes import SignInStatus
from .packet import Packet
from .packet_types import PacketType


class SignInRequest(Packet):
    def __init__(self, username: str):
        super().__init__(PacketType.SIGN_IN)

        self.append_var_len(bytes(username, encoding=ENCODING))

class SignInResponse(Packet):
    def __init__(self, status: SignInStatus):
        super().__init__(PacketType.SIGN_IN)

        self.append_bytes(bytes([status.value]))
