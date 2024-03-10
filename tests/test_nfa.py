from redfa.nfa import Nfa, find
from redfa.transition import NonCharTransition


# https://cyberzhg.github.io/toolbox/regex2nfa?regex=KGF8YikqYQ==
def test_nfa_0():
    states = set(range(9))
    transitions = {
        0: {NonCharTransition.EPSILON: {1, 7}},
        1: {NonCharTransition.EPSILON: {2, 4}},
        2: {"a": {3}},
        3: {NonCharTransition.EPSILON: {6}},
        4: {"b": {5}},
        5: {NonCharTransition.EPSILON: {6}},
        6: {NonCharTransition.EPSILON: {1, 7}},
        7: {"a": {8}}
    }
    accepts = {8}
    start = {0}
    nfa = Nfa(states, transitions, accepts, start)
    
    assert find(nfa, "a") == (0, 1)
    assert find(nfa, "b") is None
    assert find(nfa, "aa") == (0, 2)
    assert find(nfa, "ca") == (1, 2)


def make_nfa_1():
    states = set(range(16))
    transitions = {
        0: {NonCharTransition.EPSILON: {1, 9}},
        1: {"a": {2}},
        2: {NonCharTransition.EPSILON: {3, 5}},
        3: {"a": {4}},
        4: {NonCharTransition.EPSILON: {3, 5}},
        5: {NonCharTransition.EPSILON: {6, 8}},
        6: {"b": {7}},
        7: {NonCharTransition.EPSILON: {6, 8}},
        8: {NonCharTransition.EPSILON: {1, 9}},
        9: {"a": {10}},
        10: {NonCharTransition.EPSILON: {11, 13}},
        11: {"a": {12}},
        12: {NonCharTransition.EPSILON: {15}},
        13: {"b": {14}},
        14: {NonCharTransition.EPSILON: {15}}
    }
    accepts = {15}
    start = {0}
    return Nfa(states, transitions, accepts, start)


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


def make_nfa_2():
    # (11)*(00|10)*
    # test case from https://www.geeksforgeeks.org/conversion-of-epsilon-nfa-to-nfa/
    states = {0, 1, 2, 3, 4}
    starts = {0}
    transitions = {
        0: {NonCharTransition.EPSILON: {2}, "1": {1}},
        1: {"1": {0}},
        2: {"0": {3}, "1": {4}},
        3: {"0": {2}},
        4: {"0": {2}},
    }
    accepts = {2}
    return Nfa(states, transitions, accepts, starts)


def test_nfa_2():
    nfa = make_nfa_2()
    
    assert find(nfa, "") == (0, 0)
    assert find(nfa, "111111") == (0, 6)
    assert find(nfa, "1100") == (0, 4)
    # i thought it should be (1, 5) but expected behaviour is actually (0, 0)
    # try it using python's re module
    assert find(nfa, "01010") == (0, 0)


if __name__ == "__main__":
    test_nfa_2()