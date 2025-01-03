import re

from redfa.thompson import thompson
from redfa import nfa


def my_match(p: str, t: str) -> nfa.NfaMatch | None:
    r = thompson(p)
    if r is None:
        return None
    return nfa.match(r, t)
    


def test_nfagroup_0():
    m = my_match(r"(aa)*aab", "aaaab")
    assert m is not None
    assert m.all_captures() == [
        ["aaaab"],
        ["aa"]
    ]


def test_nfagroup_1():
    m = my_match(r"(a+b*)*a(a|b)", "aaaab")
    assert m is not None
    assert m.all_captures() == [
        ["aaaab"],
        ["a", "a", "a"],
        ["b"]
    ]


def test_nfagroup_2():
    m = my_match(r"(ab(cd)*ef)+", "abcdefabefabcdcdef")
    assert m is not None
    assert m.all_captures() == [
        ["abcdefabefabcdcdef"],
        ["abcdef", "abef", "abcdcdef"],
        ["cd", "cd", "cd"]
    ]


def test_nfagroup_3():
    m = my_match(r"(ab((cd)*)ef)+", "abcdefabefabcdcdef")
    assert m is not None
    assert m.all_captures() == [
        ["abcdefabefabcdcdef"],
        ["abcdef", "abef", "abcdcdef"],
        ["cd", "", "cdcd"],
        ["cd", "cd", "cd"]
    ]


def test_nfagroup_4():
    m = my_match(r"(ab((cd)*)ef)+", "buffer abcdefabefabcdcdef buffer")
    assert m is not None
    assert m.all_captures() == [
        ["abcdefabefabcdcdef"],
        ["abcdef", "abef", "abcdcdef"],
        ["cd", "", "cdcd"],
        ["cd", "cd", "cd"]
    ]


def test_nfagroupparity_0():
    p = r"(ab(cd)ef)(gh(ij)kl)"
    t = "abcdefghijkl"
    mine = my_match(p, t)
    stdlib = re.match(p, t)
    assert mine is not None and stdlib is not None
    assert mine.latest_captures()[1:] == list(stdlib.groups())


def test_nfagroupparity_1():
    p = r"(ab((cd)*)ef)+"
    t = "abcdefabefabcdcdef"
    mine = my_match(p, t)
    stdlib = re.match(p, t)
    assert mine is not None and stdlib is not None
    assert mine.latest_captures()[1:] == list(stdlib.groups())