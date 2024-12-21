from enum import Enum

class scanFlag(Enum):
    sweep = 1   # no wait
    settle = 2  # wait until stable