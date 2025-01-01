from copy import deepcopy
import typing as t

from redfa.transition import NonCharTransition, Transition, text_to_transition


class Nfa(object):
    def __init__(
        self,
        states: t.Set[int],
        transitions: t.Dict[int, t.Dict[Transition, t.Set[int]]],
        accepts: t.Set[int],
        starts: t.Set[int],
        groups: t.List[t.Tuple[int, int]] | None = None
    ) -> None:
        self.states_ = states
        self.transitions_ = transitions
        self.accepts_ = accepts
        self.starts_ = starts
        self.groups_ = groups or []
    
    def __repr__(self) -> str:
        return (
            "Nfa(" +
            f"states={self.states_}, " +
            f"transitions={self.transitions_}, " +
            f"accepts={self.accepts_}, " +
            f"start={self.starts_}, " +
            f"groups={self.groups_}" +
            ")"
        )
    
    def asdict(self) -> t.Dict[str, t.Any]:
        return {
            "states": self.states_,
            "transitions": self.transitions_,
            "accepts": self.accepts_,
            "starts": self.starts_,
            "groups": self.groups_
        }
    
    def copy(self) -> "Nfa":
        return Nfa(
            states=self.states_.copy(),
            transitions=deepcopy(self.transitions_),
            accepts=self.accepts_.copy(),
            starts=self.starts_.copy(),
            groups=self.groups_.copy()
        )
    
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
    
    def available_transitions(self, states: t.Set[int]) -> t.Set[Transition]:
        transitions: t.Set[Transition] = set()
        for state in states:
            transitions |= set(self.transitions_.get(state, dict()).keys())
        return transitions
    
    def accepts(self, state: int) -> bool:
        return state in self.accepts_
    
    def remove_unregistered_states(self) -> "Nfa":
        self.accepts_ &= self.states_
        self.starts_ &= self.states_
        self.transitions_ = {
            s: {t: ds & self.states_ for t, ds in transitions.items()}
            for s, transitions in self.transitions_.items() if s in self.states_
        }
        return self
    
    def remove_epsilon_transitions(self) -> "Nfa":
        """
        Convert this NFA-e into an NFA. This mutates and returns the current
        object. To create a new NFA from this NFA-e object, see
        `Nfa.without_epsilon_transitions`.
        """
        for state in self.states_:
            if state not in self.transitions_:
                self.transitions_[state] = {}
            epsilon_states = self.epsilon_closure({state})
            for epsilon_state in epsilon_states:
                if state == epsilon_state:
                    continue
                # replay non-epsilon transitions of epsilon_state on state
                for transition, dests in self.transitions_.get(epsilon_state, dict()).items():
                    if transition == NonCharTransition.EPSILON:
                        continue
                    if transition not in self.transitions_[state]:
                        self.transitions_[state][transition] = set()
                    self.transitions_[state][transition] |= dests
                # set state as accept if epsilon_state is accept
                if self.accepts(epsilon_state):
                    self.accepts_.add(state)
                # set epsilon_state as start if state is start
                if state in self.starts_:
                    self.starts_.add(epsilon_state)
        # remove epsilon transitions
        for state, transitions in self.transitions_.items():
            transitions.pop(NonCharTransition.EPSILON, None)
        return self.remove_deadends()
    
    def remove_unreachable(self) -> "Nfa":
        """
        Remove states that cannot be reached from a starting state.
        """
        visited: t.Set[int] = set()
        queue: t.List[int] = list(self.starting_states())
        # quick and easy bfs
        while len(queue) >= 1:
            state = queue.pop(0)
            visited.add(state)
            more: t.Set[int] = set()
            for dests in self.transitions_.get(state, dict()).values():
                more |= dests
            more -= visited
            queue.extend(more)
        self.states_ = visited
        return self.remove_unregistered_states()
    
    def remove_deadends(self) -> "Nfa":
        """
        Remove starting states if they never lead to an accept state.
        """
        deadends: t.Set[int] = set()
        for start in self.starting_states():
            visited: t.Set[int] = set()
            queue: t.List[int] = [start]
            # quick and easy bfs
            while len(queue) >= 1:
                state = queue.pop(0)
                if self.accepts(state):
                    break
                visited.add(state)
                more: t.Set[int] = set()
                for dests in self.transitions_.get(state, dict()).values():
                    more |= dests
                more -= visited
                queue.extend(more)
            else: # while loop breaks when an accept node is found
                continue
            deadends.add(start)
        self.starts_ = deadends
        return self.remove_unreachable()
    
    def without_unregistered_states(self) -> "Nfa":
        return self.copy().remove_unregistered_states()
    
    def without_epsilon_transitions(self) -> "Nfa":
        return self.copy().remove_epsilon_transitions()
    
    def without_unreachable(self) -> "Nfa":
        return self.copy().remove_unreachable()
    
    def without_deadends(self) -> "Nfa":
        return self.copy().remove_deadends()


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
    for start_index in range(len(text) + 1):
        traveller = NfaTraveller(nfa)
        traveller.travel(text[start_index:], start=(start_index == 0))
        length = traveller.length()
        if length is not None:
            return start_index, length + start_index
    return None