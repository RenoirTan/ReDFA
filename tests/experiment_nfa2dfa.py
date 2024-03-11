import sys
from pprint import pprint

from redfa.nfa2dfa import nfa2dfa
from tests.experiments import make_nfa

x = int(sys.argv[1]) if len(sys.argv) >= 2 else 1

nfa = make_nfa(x)()
dfa = nfa2dfa(nfa)
pprint(dfa.asdict())