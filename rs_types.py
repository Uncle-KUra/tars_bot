from typing import Literal
import enum

RS_Levels = Literal[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


class RedStarModes(enum.Enum):
    none = 0
    dark = 1
    duo = 2
