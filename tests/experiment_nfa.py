from pprint import pprint

from redfa.nfa import Nfa
from redfa.transition import NonCharTransition


def make_nfa_0():
    states = {0, 1, 2, 3}
    starts = {0}
    transitions = {
        0: {NonCharTransition.EPSILON: {2, 3}, "b": {1}},
    }
    accepts = {1, 3}
    return Nfa(states, transitions, accepts, starts)

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

def make_nfa_2():
    states = {0, 1, 2, 3}
    starts = {0}
    transitions = {
        0: {NonCharTransition.EPSILON: {2}, "a": {1}},
        1: {"b": {3}},
        2: {"b": {3}},
    }
    accepts = {3}
    return Nfa(states, transitions, accepts, starts)

def make_nfa_3():
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

nfa = make_nfa_3()

nfa_x = nfa.without_epsilon_transitions()
print("<-- States -->")
print(nfa_x.states_)
print("<-- Starts -->")
print(nfa_x.starts_)
print("<-- Accepts -->")
print(nfa_x.accepts_)
print("<-- Transitions -->")
pprint(nfa_x.transitions_)