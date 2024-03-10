from enum import Enum
import typing as t


class NonCharTransition(Enum):
    START = 0
    END = 1


Transition: t.TypeAlias = str | NonCharTransition


def text_to_transition(text: str, *, start: bool = True) -> t.Generator[Transition, None, None]:
    if start:
        yield NonCharTransition.START
    yield from text
    yield NonCharTransition.END