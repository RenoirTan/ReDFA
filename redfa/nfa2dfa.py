import typing as t

from redfa.dfa import Dfa
from redfa.nfa import Nfa
from redfa.transition import NonCharTransition, Transition


def nfa2dfa(nfa: Nfa) -> Dfa:
    nfa = nfa.without_deadends()
    
    def set_to_tuple(s: t.Set[int]) -> t.Tuple[int, ...]:
        l = list(s)
        l.sort()
        return tuple(l)
    
    queue: t.List[t.Set[int]] = [nfa.epsilon_closure(nfa.starting_states())]
    # mapping of nfa states to dfa states
    states_mapping: t.Dict[t.Tuple[int, ...], int] = {}
    index = 0
    transitions: t.Dict[int, t.Dict[Transition, int]] = {}
    visited: t.Set[t.Tuple[int, ...]] = set()
    
    # each state in dfa can be mapped to a set of states in nfa
    while len(queue) >= 1:
        nfa_states = queue.pop(0)
        nfa_states_tuple = set_to_tuple(nfa_states)
        
        # add nfa set of states to states mapping
        if nfa_states_tuple not in states_mapping:
            states_mapping[nfa_states_tuple] = index
            transitions[index] = {}
            index += 1
        
        # add destinations including after epsilon transitions
        for transition in nfa.available_transitions(nfa_states):
            # don't include epsilon transitions, they would have been dealt with
            # by the next step in previous iterations
            if transition == NonCharTransition.EPSILON:
                continue
            
            next_states = nfa.epsilon_closure(nfa.transition_states(nfa_states, transition))
            next_states_tuple = set_to_tuple(next_states)
            
            if next_states_tuple not in states_mapping:
                states_mapping[next_states_tuple] = index
                transitions[index] = {}
                index += 1
            
            # add transition from set a to set b
            transitions[
                states_mapping[nfa_states_tuple]
            ][transition] = states_mapping[next_states_tuple]
            
            if next_states_tuple not in visited:
                queue.append(next_states)
        visited.add(nfa_states_tuple)
    
    # any nfa set of states with at least one accept state in the set maps to
    # an accept state in dfa
    dfa_accepts = {
        d for ns, d in states_mapping.items()
        if any(map(lambda n: nfa.accepts(n), ns))
    }
    dfa_states = set(states_mapping.values())
    
    # convert nfa groups to dfa groups
    dfa_groups = []
    for s, a in nfa.groups_:
        opens = set()
        closes = set()
        for nfa_states, dfa_state in states_mapping.items():
            if s in nfa_states:
                opens.add(dfa_state)
            if a in nfa_states:
                closes.add(dfa_state)
        dfa_groups.append((opens, closes))
    
    return Dfa(dfa_states, transitions, dfa_accepts, 0, dfa_groups)