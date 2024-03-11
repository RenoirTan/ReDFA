from pprint import pprint
import sys

from tests.experiments import make_nfa

x = int(sys.argv[1]) if len(sys.argv) >= 2 else 1

nfa = make_nfa(x)()

nfa_x = nfa.without_epsilon_transitions()
print("<-- States -->")
print(nfa_x.states_)
print("<-- Starts -->")
print(nfa_x.starts_)
print("<-- Accepts -->")
print(nfa_x.accepts_)
print("<-- Transitions -->")
pprint(nfa_x.transitions_)