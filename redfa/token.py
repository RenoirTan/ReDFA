from enum import Enum
import typing as t


class SpecialToken(Enum):
    Backslash = 0
    OpenRoundBracket = 1
    CloseRoundBracket = 2
    Pipe = 3
    Caret = 4
    Dollar = 5,
    Star = 6,
    Plus = 7


Token: t.TypeAlias = str | SpecialToken


# First item is the token returned if not escaped
# Second item is escaped
SPECIALS: t.Dict[str, t.Tuple[Token, Token]] = {
    "(": (SpecialToken.OpenRoundBracket, "("),
    ")": (SpecialToken.CloseRoundBracket, ")"),
    "|": (SpecialToken.Pipe, "|"),
    "^": (SpecialToken.Caret, "^"),
    "$": (SpecialToken.Dollar, "$"),
    "*": (SpecialToken.Star, "*"),
    "+": (SpecialToken.Plus, "+"),
}
SPECIAL_CHARS = set(SPECIALS.keys())


def tokenize(regex: str) -> t.Generator[Token, None, None]:
    escaped = False
    for c in regex:
        if c == "\\":
            if escaped:
                yield c
            escaped = not escaped
        elif c in SPECIALS:
            yield SPECIALS[c][int(escaped)]
            escaped = False
        else:
            if escaped:
                raise ValueError(f"{repr(c)} cannot be escaped")
            yield c