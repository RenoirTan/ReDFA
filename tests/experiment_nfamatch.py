from pprint import pprint

from redfa import nfa
from redfa.thompson import thompson

p = r"(ab((cd)*)ef)+"
# p = r"(a+b*)*a(a|b)"
# p = r"(aa)*aab"
r = thompson(p)

assert r is not None

print(r)
pprint(r.transitions_)
# pprint(r.reversed_transitions())

t = "abcdefabefabcdcdef"
m = nfa.match(r, t)

# pprint(nfa.traveller.history_)
# pprint(nfa.traveller.possible_trail())

assert m is not None

print(m.span_)
print(t[m.span_[0]:m.span_[1]])
pprint(m.groups_)

for _, matches in m.groups_.items():
    for b, e in matches:
        print(t[b:e])