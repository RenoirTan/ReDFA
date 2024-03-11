from pprint import pprint

from tests.experiments import make_nfa_1

nfa = make_nfa_1()

nfa_x = nfa.without_epsilon_transitions()
print("<-- States -->")
print(nfa_x.states_)
print("<-- Starts -->")
print(nfa_x.starts_)
print("<-- Accepts -->")
print(nfa_x.accepts_)
print("<-- Transitions -->")
pprint(nfa_x.transitions_)