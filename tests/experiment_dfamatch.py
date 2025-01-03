from pprint import pprint
from redfa import dfa, nfa
from redfa.nfa2dfa import nfa2dfa
from redfa.thompson import thompson


p = r"(ab((cd)*)ef)+"
n = thompson(p)
assert n is not None
print("=== NFA ===")
print(n)
pprint(n.transitions_)
print("=== DFA ===")
d = nfa2dfa(n)
print(d)
pprint(d.transitions_)
print("=== RESULT ===")
m = dfa.match(d, "abcdefabefabcdcdef")
assert m is not None
print(m.substr())
pprint(m.groups_)
pprint(m.all_captures())