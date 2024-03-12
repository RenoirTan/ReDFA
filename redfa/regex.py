import typing as t

from redfa.dfa import Dfa, find as dfa_find
from redfa.exception import MalformedRegexError
from redfa.nfa2dfa import nfa2dfa
from redfa.thompson import thompson


__all__ = ["Regex", "compile", "find"]


class Regex(object):
    def __init__(self, automaton: Dfa) -> None:
        self.automaton = automaton

    def find(self, text: str) -> t.Tuple[int, int] | None:
        return dfa_find(self.automaton, text)


def compile(regex: str) -> Regex:
    nfa = thompson(regex)
    if nfa is None:
        raise MalformedRegexError("could not parse regex")
    return Regex(nfa2dfa(nfa))


def find(regex: str, text: str) -> t.Tuple[int, int] | None:
    return compile(regex).find(text)