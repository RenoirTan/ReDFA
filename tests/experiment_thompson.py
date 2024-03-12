from pprint import pprint
import sys
from redfa.nfa2dfa import nfa2dfa

from redfa.thompson import thompson

regex = sys.argv[1] if len(sys.argv) >= 2 else "ab"

nfa = thompson(regex)
if nfa is None:
    print("uh oh")
    sys.exit(1)
pprint(nfa.asdict())
pprint(nfa2dfa(nfa).asdict())