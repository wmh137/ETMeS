from enum import Enum, IntEnum

class insType(Enum):
    visa = 1
    other = 0

class SM(IntEnum):
    V  = 0
    I  = 1

class waitFlag(IntEnum):
    stable = 0
    positive = 1
    negative = -1
