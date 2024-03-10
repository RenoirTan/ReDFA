import typing as t

from redfa.transition import NonCharTransition, Transition, text_to_transition


class Nfa(object):
    def __init__(
        self,
        states: t.Set[int],
        transitions: t.Dict[int, t.Dict[Transition, t.Set[int]]],
        accepts: t.Set[int],
        starts: t.Set[int]
    ) -> None:
        self.states_ = states
        self.transitions_ = transitions
        self.accepts_ = accepts
        self.starts_ = starts
    
    def starting_states(self) -> t.Set[int]:
        return self.starts_.copy()
    
    def transition(self, state: int, transition: Transition) -> t.Set[int]:
        default_out = {state} if type(transition) == NonCharTransition else set()
        return self.transitions_.get(state, dict()).get(transition, default_out)
    
    def epsilon_closure(self, srcs: t.Set[int]) -> t.Set[int]:
        """
        Get the set of states reachable from the states in `srcs` via only
        epsilon transitions.
        """
        frontier = srcs.copy()
        # Don't revisit these states
        visited = set()
        while True:
            # Visit unvisited states in the frontier
            frontier -= visited
            # No more to check, exit
            if len(frontier) <= 0:
                break
            # Get next set of states after epsilon transition, store in dest
            dests = self.transition_states(frontier, NonCharTransition.EPSILON)
            # Mark frontier as visited
            visited |= frontier
            # Use dests as the next frontier, this is the recursive step
            frontier = dests
        return srcs | visited
    
    def transition_states(self, states: t.Set[int], transition: Transition) -> t.Set[int]:
        dests = set()
        for state in states:
            dests |= self.transition(state, transition)
        return dests
    
    def accepts(self, state: int) -> bool:
        return state in self.accepts_
    
    def without_epsilon_transitions(self) -> "Nfa":
        # any states that can be reached from any starting state via only
        # epsilon closures should also be starting states
        new_starts = self.epsilon_closure(self.starting_states())
        
        # any destination states that can be reached from a source state
        # including via epsilon-only transitions, should also have a directed
        # edge from src to dest
        new_transitions: t.Dict[int, t.Dict[Transition, t.Set[int]]] = {}
        for state in self.states_:
            ts: t.Dict[Transition, t.Set[int]] = {}
            new_transitions[state] = ts
            if state not in self.transitions_:
                continue
            for transition, dests in self.transitions_[state].items():
                # get all reachable states including after epsilon transitions
                dests = self.epsilon_closure(dests)
                ts[transition] = dests

        # remove all epsilon transitions
        for state, transitions in new_transitions.items():
            transitions.pop(NonCharTransition.EPSILON, None)

        # remove all non-accept state with no transitions FROM it
        new_transitions = {
            s: t for s, t in new_transitions.items()
            if s in self.accepts_ or len(t) >= 1
        }
        
        new_states = set(new_transitions.keys())
        # remove states from transitions that have disappeared
        for state, transitions in new_transitions.items():
            for transition in transitions.keys():
                transitions[transition] &= new_states
        new_starts &= new_states
        new_accepts = self.accepts_ & new_states
        return Nfa(
            states=new_states,
            transitions=new_transitions,
            accepts=new_accepts,
            starts=new_starts
        )


# copied from https://en.wikipedia.org/wiki/Nondeterministic_finite_automaton#Example
class NfaTraveller(object):
    def __init__(self, nfa: Nfa) -> None:
        self.nfa_ = nfa
        self.history_: t.List[t.Tuple[t.Set[int], int]] = [(nfa.starting_states(), 0)]
    
    def consume_epsilon(self):
        """
        If the current states have epsilon transitions, add the destinations to
        the set of current states. Do this recursively.
        """
        srcs = self.history_[-1][0]
        self.history_[-1] = (self.nfa_.epsilon_closure(srcs), self.history_[-1][1])
    
    def consume(self, transition: Transition) -> bool:
        dests = self.nfa_.transition_states(self.history_[-1][0], transition)
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
    