import typing as t

from redfa.transition import NonCharTransition, Transition, text_to_transition


class Nfa(object):
    def __init__(
        self,
        states: t.Set[int],
        transitions: t.Dict[int, t.Dict[Transition, t.Set[int]]],
        accepts: t.Set[int],
        start: int
    ) -> None:
        self.states_ = states
        self.transitions_ = transitions
        self.accepts_ = accepts
        self.start_ = start
    
    def start(self) -> int:
        return self.start_
    
    def transition(self, state: int, transition: Transition) -> t.Set[int]:
        return self.transitions_.get(state, dict()).get(transition, set())
    
    def accepts(self, state: int) -> bool:
        return state in self.accepts_
    
    def epsilonable_states(self, states: t.Set[int]) -> t.Set[int]:

        def state_has_epsilon(state: int) -> bool:
            return len(self.transition(state, NonCharTransition.EPSILON)) >= 1
        
        return set(filter(state_has_epsilon, states))
    

# copied from https://en.wikipedia.org/wiki/Nondeterministic_finite_automaton#Example
class NfaTraveller(object):
    def __init__(self, nfa: Nfa) -> None:
        self.nfa_ = nfa
        self.history_: t.List[t.Tuple[t.Set[int], int]] = [({nfa.start()}, 0)]
    
    def consume_epsilon(self):
        frontier = self.nfa_.epsilonable_states(self.history_[-1][0])
        visited = set()
        while True:
            frontier -= visited
            if len(frontier) <= 0:
                break
            dests = set()
            for state in frontier:
                dests |= self.nfa_.transition(state, NonCharTransition.EPSILON)
            visited |= frontier
            frontier = dests
        self.history_[-1] = (self.history_[-1][0] | visited, self.history_[-1][1])
    
    def consume(self, transition: Transition) -> bool:
        dests: t.Set[int] = set()
        for state in self.history_[-1][0]:
            dests |= self.nfa_.transition(state, transition)
        if len(dests) <= 0:
            return False
        substr_len = self.history_[-1][1]
        if type(transition) == str:
            substr_len += 1
        self.history_.append((dests, substr_len))
        return True
    
    def travel(self, text: str, *, start: bool = True):
        self.consume_epsilon()
        for transition in text_to_transition(text, start=start):
            if not self.consume(transition):
                break
            self.consume_epsilon()
    
    def length(self) -> int | None:
        for states, substr_len in self.history_[::-1]:
            if any(map(lambda s: self.nfa_.accepts(s), states)):
                return substr_len
        return None


def find(nfa: Nfa, text: str) -> t.Tuple[int, int] | None:
    for start_index in range(len(text)):
        traveller = NfaTraveller(nfa)
        traveller.travel(text[start_index:], start=(start_index == 0))
        length = traveller.length()
        if length is not None:
            return start_index, length + start_index
    return None
    