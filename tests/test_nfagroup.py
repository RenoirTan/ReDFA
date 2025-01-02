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