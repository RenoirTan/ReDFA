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


if __name__ == "__main__":
    test_dfa_0()