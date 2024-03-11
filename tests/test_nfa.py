from redfa.nfa import Nfa, find
from redfa.transition import NonCharTransition
from tests.experiments import make_nfa_0, make_nfa_1, make_nfa_2, make_nfa_3, make_nfa_4


# https://cyberzhg.github.io/toolbox/regex2nfa?regex=KGF8YikqYQ==
def test_nfa_0():
    nfa = make_nfa_0()
    
    assert find(nfa, "a") == (0, 1)
    assert find(nfa, "b") is None
    assert find(nfa, "aa") == (0, 2)
    assert find(nfa, "ca") == (1, 2)


# https://cyberzhg.github.io/toolbox/nfa2dfa?regex=KGErYiopKmEoYXxiKQ==
# (a+b*)*a(a|b)
def test_nfa_1():
    nfa = make_nfa_1()
    
    assert find(nfa, "aabab") == (0, 5)
    assert find(nfa, "c") is None
    assert find(nfa, "baab") == (1, 4)
    assert find(nfa, "acb") is None


def test_nfa_1_no_epsilon():
    nfa = make_nfa_1().without_epsilon_transitions()
    
    assert find(nfa, "aabab") == (0, 5)
    assert find(nfa, "c") is None
    assert find(nfa, "baab") == (1, 4)
    assert find(nfa, "acb") is None


def test_nfa_2():
    nfa = make_nfa_2()
    
    assert find(nfa, "aaaa") is None
    assert find(nfa, "baa") == (0, 1)
    assert find(nfa, "aaab") == (2, 4)
    assert find(nfa, "bab") == (0, 1)


def test_nfa_2_no_epsilon():
    nfa = make_nfa_2().without_epsilon_transitions()
    
    assert find(nfa, "aaaa") is None
    assert find(nfa, "baa") == (0, 1)
    assert find(nfa, "aaab") == (2, 4)
    assert find(nfa, "bab") == (0, 1)


def test_nfa_3():
    nfa = make_nfa_3()
    
    assert find(nfa, "") == (0, 0)
    assert find(nfa, "111111") == (0, 6)
    assert find(nfa, "1100") == (0, 4)
    # i thought it should be (1, 5) but expected behaviour is actually (0, 0)
    # try it using python's re module
    assert find(nfa, "01010") == (0, 0)


def test_nfa_3_no_epsilon():
    nfa = make_nfa_3().without_epsilon_transitions()
    
    assert find(nfa, "") == (0, 0)
    assert find(nfa, "111111") == (0, 6)
    assert find(nfa, "1100") == (0, 4)
    assert find(nfa, "01010") == (0, 0)


if __name__ == "__main__":
    test_nfa_3()