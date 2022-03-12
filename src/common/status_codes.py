from enum import Enum, unique


@unique
class SignInStatus(Enum):
    OK = 0
    USED_USERNAME = 1
    INVALID_USERNAME = 2
