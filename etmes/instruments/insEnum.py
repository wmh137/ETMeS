from enum import Enum

class eEnum(Enum):
    def __str__(self):
        return self.name
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.name == value:
                    return member
        return super()._missing_(value)

class insType(eEnum):
    visa = 1
    other = 0

class SM(int, eEnum):
    V  = 0
    I  = 1

class waitFlag(int, eEnum):
    stable = 0
    positive = 1
    negative = -1
