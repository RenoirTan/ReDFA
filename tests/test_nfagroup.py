from redfa.thompson import thompson
from redfa import nfa


def get_groups_from_match(m: nfa.NfaMatch):
    groups = []
    for group_arr in m.groups_.values():
        groups.extend(group_arr)
    return sorted([m.string_[b:e] for b, e in groups])


def test_nfagroup_0():
    r = thompson(r"(aa)*aab")
    assert r is not None
    m = nfa.match(r, "aaaab")
    assert m is not None
    assert get_groups_from_match(m) == ["aa"]


def test_nfagroup_1():
    r = thompson(r"(a+b*)*a(a|b)")
    assert r is not None
    m = nfa.match(r, "aaaab")
    assert m is not None
    assert get_groups_from_match(m) == ["a", "a", "a", "b"]


def test_nfagroup_2():
    r = thompson(r"(ab(cd)*ef)+")
    assert r is not None
    m = nfa.match(r, "abcdefabefabcdcdef")
    assert m is not None
    assert get_groups_from_match(m) == ["abcdcdef", "abcdef", "abef", "cd", "cd", "cd"]


def test_nfagroup_3():
    r = thompson(r"(ab((cd)*)ef)+")
    assert r is not None
    m = nfa.match(r, "abcdefabefabcdcdef")
    assert m is not None
    assert get_groups_from_match(m) == [
        "", "abcdcdef", "abcdef", "abef", "cd", "cd", "cd", "cd", "cdcd"
    ]