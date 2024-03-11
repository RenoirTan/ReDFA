from copy import deepcopy
from pprint import pformat
import typing as t

from redfa.transition import NonCharTransition, Transition, text_to_transition


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
    
    def __repr__(self) -> str:
        return (
            "Dfa(" +
            f"states={self.states_}, " +
            f"transitions={self.transitions_}, " +
            f"accepts={self.accepts_}, " +
            f"start={self.start_}" +
            ")"
        )
    
    def asdict(self) -> t.Dict[str, t.Any]:
        return {
            "states": self.states_,
            "transitions": self.transitions_,
            "accepts": self.accepts_,
            "start": self.start_
        }
    
    def copy(self) -> "Dfa":
        return Dfa(
            states=self.states_.copy(),
            transitions=deepcopy(self.transitions_),
            accepts=self.accepts_.copy(),
            start=self.start_
        )
    
    def start(self) -> int:
        return self.start_
    
    def transition(self, state: int, transition: Transition) -> int | None:
        if state not in self.states_:
            return None
        edges = self.transitions_.get(state, dict())
        default_out = state if type(transition) == NonCharTransition else None
        dest = edges.get(transition, default_out)
        return dest
    
    def accepts(self, state: int) -> bool:
        return state in self.accepts_
    
    def remove_unregistered_states(self) -> "Dfa":
        if self.start_ not in self.states_:
            raise ValueError("start not in states")
        self.accepts_ &= self.states_
        self.transitions_ = {
            s: {t: d for t, d in transitions.items() if d in self.states_}
            for s, transitions in self.transitions_.items() if s in self.states_
        }
        return self
    
    def remove_unreachable_states(self) -> "Dfa":
        visited: t.Set[int] = set()
        queue: t.List[int] = [self.start_]
        while len(visited) >= 1:
            state = queue.pop(0)
            visited.add(state)
            for d in self.transitions_.get(state, dict()).values():
                if d not in visited:
                    queue.append(d)
        self.states_ = visited
        return self.remove_unregistered_states()

    def without_unregistered_states(self) -> "Dfa":
        return self.copy().remove_unregistered_states()
    
    def without_unreachable_states(self) -> "Dfa":
        return self.copy().remove_unreachable_states()


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
    for start_index in range(len(text) + 1):
        traveller = DfaTraveller(dfa)
        traveller.travel(text[start_index:], start=(start_index == 0))
        length = traveller.length()
        if length is not None:
            return start_index, length + start_index
    return None