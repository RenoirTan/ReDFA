from redfa.dfa import Dfa, find
from redfa.transition import NonCharTransition


def test_dfa_0():
    # /(a|b)*a/
    states = {0, 1, 2}
    transitions = {
        0: {"a": 1, "b": 2},
        1: {"a": 1, "b": 2},
        2: {"a": 1, "b": 2}
    }
    accepts = {1}
    start = 0
    dfa = Dfa(states, transitions, accepts, start)
    
    assert find(dfa, "a") == (0, 1)
    assert find(dfa, "b") is None
    assert find(dfa, "aa") == (0, 2)
    assert find(dfa, "ca") == (1, 2)


def test_dfa_1():
    # /(11)*(00|10)*/
    # https://cyberzhg.github.io/toolbox/nfa2dfa?regex=KDExKSooMDB8MTApKg==
    states = {0, 1, 2, 3, 4, 5, 6}
    transitions = {
        0: {"0": 1, "1": 2},
        1: {"0": 3},
        2: {"0": 4, "1": 5},
        3: {"0": 1, "1": 6},
        4: {"0": 1, "1": 6},
        5: {"0": 1, "1": 2},
        6: {"0": 4}
    }
    accepts = {0, 3, 4, 5}
    start = 0
    dfa = Dfa(states, transitions, accepts, start)
    
    assert find(dfa, "") == (0, 0)
    assert find(dfa, "111111") == (0, 6)
    assert find(dfa, "1100") == (0, 4)
    assert find(dfa, "01010") == (0, 0)


if __name__ == "__main__":
    test_dfa_0()