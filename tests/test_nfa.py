from redfa.nfa import Nfa, find
from redfa.transition import NonCharTransition


def test_nfa_0():
    states = set(range(9))
    transitions = {
        0: {NonCharTransition.START: {0}, NonCharTransition.EPSILON: {1, 7}},
        1: {NonCharTransition.EPSILON: {2, 4}},
        2: {"a": {3}},
        3: {NonCharTransition.EPSILON: {6}},
        4: {"b": {5}},
        6: {NonCharTransition.EPSILON: {1, 7}},
        7: {"a": {8}}
    }
    accepts = {8}
    start = 0
    nfa = Nfa(states, transitions, accepts, start)
    
    assert find(nfa, "a") == (0, 1)
    assert find(nfa, "b") is None
    assert find(nfa, "aa") == (0, 2)
    assert find(nfa, "ca") == (1, 2)