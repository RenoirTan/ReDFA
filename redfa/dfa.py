import typing as t

from redfa.transition import Transition, text_to_transition


class Dfa(object):
    def __init__(
        self,
        states: t.Set[int],
        transitions: t.Dict[int, t.Dict[Transition, int]],
        accepts: t.Set[int],
        start: int
    ) -> None:
        self.states_ = states
        self.transitions_ = transitions
        self.accepts_ = accepts
        self.start_ = start
    
    def start(self) -> int:
        return self.start_
    
    def transition(self, state: int, transition: Transition) -> int | None:
        if state not in self.states_:
            return None
        edges = self.transitions_.get(state, dict())
        dest = edges.get(transition)
        return dest
    
    def accepts(self, state: int) -> bool:
        return state in self.accepts_


class DfaTraveller(object):
    def __init__(self, dfa: Dfa) -> None:
        self.dfa_ = dfa
        # first item in tuple is last state, second item is length of substring
        self.states_: t.List[t.Tuple[int, int]] = [(dfa.start(), 0)]
    
    def consume(self, transition: Transition) -> bool:
        src, substr_len = self.states_[-1]
        dest = self.dfa_.transition(src, transition)
        if dest is None:
            return False
        if type(transition) == str:
            substr_len += 1
        self.states_.append((dest, substr_len))
        return True
    
    def travel(self, text: str, *, start: bool = True):
        for transition in text_to_transition(text, start=start):
            if not self.consume(transition):
                break
    
    def length(self) -> int | None:
        for state, substr_len in self.states_[::-1]:
            if self.dfa_.accepts(state):
                return substr_len
        return None


def find(dfa: Dfa, text: str) -> t.Tuple[int, int] | None:
    for start_index in range(len(text)):
        traveller = DfaTraveller(dfa)
        traveller.travel(text[start_index:], start=(start_index == 0))
        length = traveller.length()
        if length is not None:
            return start_index, length + start_index
    return None