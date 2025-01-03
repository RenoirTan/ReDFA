from copy import deepcopy
import typing as t

from redfa.transition import NonCharTransition, Transition, text_to_transition


class Dfa(object):
    def __init__(
        self,
        states: t.Set[int],
        transitions: t.Dict[int, t.Dict[Transition, int]],
        accepts: t.Set[int],
        start: int,
        groups: t.List[t.Tuple[t.Set[int], t.Set[int]]] | None = None
    ) -> None:
        self.states_ = states
        self.transitions_ = transitions
        self.accepts_ = accepts
        self.start_ = start
        self.groups_: t.List[t.Tuple[t.Set[int], t.Set[int]]] = groups or []
    
    def __repr__(self) -> str:
        return (
            "Dfa(" +
            f"states={self.states_}, " +
            f"transitions={self.transitions_}, " +
            f"accepts={self.accepts_}, " +
            f"start={self.start_}, " +
            f"groups={self.groups_}" +
            ")"
        )
    
    def asdict(self) -> t.Dict[str, t.Any]:
        return {
            "states": self.states_,
            "transitions": self.transitions_,
            "accepts": self.accepts_,
            "start": self.start_,
            "groups": self.groups_
        }
    
    def copy(self) -> "Dfa":
        return Dfa(
            states=self.states_.copy(),
            transitions=deepcopy(self.transitions_),
            accepts=self.accepts_.copy(),
            start=self.start_,
            groups=deepcopy(self.groups_)
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
        self.history_: t.List[t.Tuple[int, int]] = [(dfa.start(), 0)]
    
    def consume(self, transition: Transition) -> bool:
        src, substr_len = self.history_[-1]
        dest = self.dfa_.transition(src, transition)
        if dest is None:
            return False
        if type(transition) == str:
            substr_len += 1
        self.history_.append((dest, substr_len))
        return True
    
    def travel(self, text: str, *, start: bool = True):
        for transition in text_to_transition(text, start=start):
            if not self.consume(transition):
                break
    
    def length(self) -> int | None:
        for state, substr_len in self.history_[::-1]:
            if self.dfa_.accepts(state):
                return substr_len
        return None
    
    def find_groups(self, *, offset: int = 0) -> t.List[t.List[t.Tuple[int, int]]]:
        result = []
        for opens, closes in self.dfa_.groups_:
            spans = []
            closed = True
            prev_i = None
            for state, i in self.history_:
                if prev_i == i:
                    continue
                def new_span():
                    nonlocal closed
                    if state in opens:
                        spans.append((offset + i, -1))
                        closed = False
                
                def close_span():
                    nonlocal closed
                    if state in closes:
                        b, _ = spans[-1]
                        spans[-1] = b, offset + i
                        closed = True
                
                if closed:
                    new_span()
                    close_span()
                else:
                    close_span()
                    new_span()
                prev_i = i
            result.append([(b, e) for b, e in spans if e != -1])
        return result


def find(dfa: Dfa, text: str) -> t.Tuple[int, int] | None:
    for start_index in range(len(text) + 1):
        traveller = DfaTraveller(dfa)
        traveller.travel(text[start_index:], start=(start_index == 0))
        length = traveller.length()
        if length is not None:
            return start_index, length + start_index
    return None


class DfaMatch(object):
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


def match(dfa: Dfa, text: str) -> DfaMatch | None:
    for start_index in range(len(text) + 1):
        traveller = DfaTraveller(dfa)
        traveller.travel(text[start_index:], start=(start_index == 0))
        length = traveller.length()
        if length is not None:
            return DfaMatch(
                string=text,
                span=(start_index, length + start_index),
                groups=traveller.find_groups(offset=start_index)
            )
    return None