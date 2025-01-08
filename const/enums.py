from enum import Enum

class Region(Enum):
    CN = 0
    TW = 1
    KR = 2

class Processing(Enum):
    NO = 0
    MOD = 1
    LAUNCHER = 2
    CLIENT = 3
    HOTFIX = 4