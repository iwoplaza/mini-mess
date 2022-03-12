from enum import Enum, unique


@unique
class ClientMode(Enum):
    SIGNING_IN = 0
    CHAT = 1
