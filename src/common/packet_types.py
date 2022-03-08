from enum import Enum, unique


@unique
class PacketType(Enum):
    SIGN_IN = 0  # Sign-in Request/Response
    USER_JOINED = 1
    USER_LEFT = 2
    MESSAGE = 10
