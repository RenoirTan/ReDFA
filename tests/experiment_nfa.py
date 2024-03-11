from pprint import pprint
import sys

from tests.experiments import make_nfa

x = int(sys.argv[1]) if len(sys.argv) >= 2 else 1

nfa = make_nfa(x)()

nfa_x = nfa.without_epsilon_transitions()
pprint(nfa_x.asdict())