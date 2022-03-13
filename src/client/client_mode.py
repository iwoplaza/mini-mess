from enum import Enum, unique


@unique
class ClientMode(Enum):
    CONNECTING = 0
    SIGNING_IN = 1
    CHAT = 2
