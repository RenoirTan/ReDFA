import re

from redfa.dfa import DfaMatch
from redfa.regex import compile


def my_match(p: str, t: str) -> DfaMatch | None:
    r = compile(p)
    if r is None:
        return None
    return r.match(t)


def test_group_0():
    m = my_match(r"(aa)*aab", "aaaab")
    assert m is not None
    assert m.all_captures() == [
        ["aaaab"],
        ["aa"]
    ]


def test_group_1():
    m = my_match(r"(a+b*)*a(a|b)", "aaaab")
    assert m is not None
    assert m.all_captures() == [
        ["aaaab"],
        ["a", "a", "a"],
        ["b"]
    ]


def test_group_2():
    m = my_match(r"(ab(cd)*ef)+", "abcdefabefabcdcdef")
    assert m is not None
    assert m.all_captures() == [
        ["abcdefabefabcdcdef"],
        ["abcdef", "abef", "abcdcdef"],
        ["cd", "cd", "cd"]
    ]


def test_group_3():
    m = my_match(r"(ab((cd)*)ef)+", "abcdefabefabcdcdef")
    assert m is not None
    assert m.all_captures() == [
        ["abcdefabefabcdcdef"],
        ["abcdef", "abef", "abcdcdef"],
        ["cd", "", "cdcd"],
        ["cd", "cd", "cd"]
    ]


def test_group_4():
    m = my_match(r"(ab((cd)*)ef)+", "buffer abcdefabefabcdcdef buffer")
    assert m is not None
    assert m.all_captures() == [
        ["abcdefabefabcdcdef"],
        ["abcdef", "abef", "abcdcdef"],
        ["cd", "", "cdcd"],
        ["cd", "cd", "cd"]
    ]


def test_groupparity_0():
    p = r"(ab(cd)ef)(gh(ij)kl)"
    t = "abcdefghijkl"
    mine = my_match(p, t)
    stdlib = re.match(p, t)
    assert mine is not None and stdlib is not None
    assert mine.latest_captures()[1:] == list(stdlib.groups())


def test_groupparity_1():
    p = r"(ab((cd)*)ef)+"
    t = "abcdefabefabcdcdef"
    mine = my_match(p, t)
    stdlib = re.match(p, t)
    assert mine is not None and stdlib is not None
    assert mine.latest_captures()[1:] == list(stdlib.groups())