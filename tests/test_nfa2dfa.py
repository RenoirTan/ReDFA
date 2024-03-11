from redfa.dfa import find
from redfa.nfa2dfa import nfa2dfa
from tests.experiments import make_nfa_0, make_nfa_1, make_nfa_2, make_nfa_3


def test_nfa2dfa_0():
    dfa = nfa2dfa(make_nfa_0())
    
    assert find(dfa, "a") == (0, 1)
    assert find(dfa, "b") is None
    assert find(dfa, "aa") == (0, 2)
    assert find(dfa, "ca") == (1, 2)


def test_nfa2dfa_1():
    dfa = nfa2dfa(make_nfa_1())
    
    assert find(dfa, "aabab") == (0, 5)
    assert find(dfa, "c") is None
    assert find(dfa, "baab") == (1, 4)
    assert find(dfa, "acb") is None


def test_nfa2dfa_2():
    dfa = nfa2dfa(make_nfa_2())
    
    assert find(dfa, "aaaa") is None
    assert find(dfa, "baa") == (0, 1)
    assert find(dfa, "aaab") == (2, 4)
    assert find(dfa, "bab") == (0, 1)


def test_nfa2dfa_3():
    dfa = nfa2dfa(make_nfa_3())
    
    assert find(dfa, "") == (0, 0)
    assert find(dfa, "111111") == (0, 6)
    assert find(dfa, "1100") == (0, 4)
    # i thought it should be (1, 5) but expected behaviour is actually (0, 0)
    # try it using python's re module
    assert find(dfa, "01010") == (0, 0)