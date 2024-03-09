from enum import Enum
import typing as t


class NonCharTransition(Enum):
    START = 0
    END = 1


Transition: t.TypeAlias = str | NonCharTransition