import typing as t

from redfa.dfa import Dfa, DfaMatch, find as dfa_find, match as dfa_match
from redfa.exception import MalformedRegexError
from redfa.nfa import Nfa, find as nfa_find, match as nfa_match
from redfa.nfa2dfa import nfa2dfa
from redfa.thompson import thompson


__all__ = ["Regex", "compile", "find"]


class Match(object):
    def __init__(
        self,
        string: str,
        span: t.Tuple[int, int],
        groups: t.List[t.List[t.Tuple[int, int]]]
    ) -> None:
        self.string_ = string
        self.span_ = span
        self.groups_ = groups
    
    def substr(self) -> str:
        b, e = self.span_
        return self.string_[b:e]
    
    def latest_captures(self) -> t.List[str]:
        captures = [self.substr()]
        for spans in self.groups_:
            if not spans:
                captures.append("")
                continue
            b, e = spans[-1]
            captures.append(self.string_[b:e])
        return captures
    
    def all_captures(self) -> t.List[t.List[str]]:
        captures = [[self.substr()]]
        for spans in self.groups_:
            captures.append([self.string_[b:e] for b, e in spans])
        return captures


class Regex(object):
    def __init__(self, automaton: Dfa | Nfa) -> None:
        self.automaton: Dfa | Nfa = automaton

    def find(self, text: str) -> t.Tuple[int, int] | None:
        if type(self.automaton) == Dfa:
            return dfa_find(self.automaton, text)
        elif type(self.automaton) == Nfa:
            return nfa_find(self.automaton, text)
    
    def match(self, text: str) -> Match | None:
        if type(self.automaton) == Dfa:
            raise NotImplemented
        elif type(self.automaton) == Nfa:
            nm = nfa_match(self.automaton, text)
            if nm is None:
                return None
            return Match(
                string=nm.string_,
                span=nm.span_,
                groups=nm.groups()
            )


def compile(regex: str) -> Regex:
    nfa = thompson(regex)
    if nfa is None:
        raise MalformedRegexError("could not parse regex")
    if nfa.groups_:
        return Regex(nfa)
    else:
        return Regex(nfa2dfa(nfa))


def find(regex: str, text: str) -> t.Tuple[int, int] | None:
    return compile(regex).find(text)