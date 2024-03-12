import typing as t

from redfa.nfa import Nfa
from redfa.transition import NonCharTransition, Transition


def _empty_expression() -> Nfa:
    return Nfa(
        states={0, 1},
        transitions={0: {NonCharTransition.EPSILON: {1}}},
        accepts={1},
        starts={0}
    )


def _symbol_expression(char: Transition) -> Nfa:
    return Nfa(
        states={0, 1},
        transitions={0: {char: {1}}},
        accepts={1},
        starts={0}
    )


def _kleene_plus_expression(expression: Nfa) -> Nfa:
    if len(expression.starts_) != 1 or len(expression.accepts_) != 1:
        raise ValueError("expression must have only one accept state and one start state.")
    expression = expression.copy()
    # create a loop from accept to start
    start = next(iter(expression.starts_))
    accept = next(iter(expression.accepts_))
    if accept not in expression.transitions_:
        expression.transitions_[accept] = {}
    if NonCharTransition.EPSILON not in expression.transitions_[accept]:
        expression.transitions_[accept][NonCharTransition.EPSILON] = set()
    expression.transitions_[accept][NonCharTransition.EPSILON].add(start)
    return expression


def _kleene_star_expression(expression: Nfa) -> Nfa:
    return _join_nfa(_empty_expression(), _kleene_plus_expression(expression), 0, 1)


def _union_expression(expressions: t.Iterable[Nfa]) -> Nfa:
    primary = Nfa(
        states={0, 1},
        transitions={},
        accepts={1},
        starts={0}
    )
    for expression in expressions:
        _join_nfa(primary, expression, 0, 1)
    return primary


def _concatenate_nfa(primary: Nfa, secondary: Nfa) -> Nfa:
    if (
        len(primary.starts_) != 1 or
        len(primary.accepts_) != 1 or
        len(secondary.starts_) != 1 or
        len(secondary.accepts_) != 1
    ):
        raise ValueError(
            "primary and secondary each must have only one accept state and one start state."
        )
    offset = max(primary.states_) + 1
    offsetter = lambda s: s + offset
    
    # add secondary states to primary
    primary.states_ |= set(map(offsetter, secondary.states_))
    
    # add transitions from secondary
    for s, transitions in secondary.transitions_.items():
        primary.transitions_[offsetter(s)] = {
            t: set(map(offsetter, ds)) for t, ds in transitions.items()
        }
    
    # convert all references to primary.accepts_ to secondary.starts_
    start = offsetter(next(iter(secondary.starts_)))
    accept = next(iter(primary.accepts_))
    if start not in primary.transitions_:
        primary.transitions_[start] = {}
    for transition, dests in primary.transitions_.get(accept, dict()).items():
        primary.transitions_[start][transition] = (
            primary.transitions_[start].get(transition, set()) | dests
        )
    for transitions in primary.transitions_.values():
        for dests in transitions.values():
            dests.discard(accept)
            dests.add(start)
    
    # set secondary.accepts_ as primary.accepts_
    primary.accepts_ = secondary.accepts_.copy()
    
    return primary


def _join_nfa(primary: Nfa, secondary: Nfa, start: int, end: int) -> Nfa:
    """
    Mutates primary such that secondary is included inside it.
    Assumes that there is only one accept state and one start state in
    secondary.
    """
    if len(secondary.starts_) != 1 or len(secondary.accepts_) != 1:
        raise ValueError("secondary must have only one accept state and one start state.")
    offset = max(primary.states_) + 1
    offsetter = lambda s: s + offset
    
    # add secondary states to primary
    primary.states_ |= set(map(offsetter, secondary.states_))
    
    # join primary[start] to secondary.starts_
    if start not in primary.transitions_:
        primary.transitions_[start] = {}
    if NonCharTransition.EPSILON not in primary.transitions_[start]:
        primary.transitions_[start][NonCharTransition.EPSILON] = set()
    primary.transitions_[start][NonCharTransition.EPSILON] |= set(map(offsetter, secondary.starts_))
    
    # add transitions from secondary
    for s, transitions in secondary.transitions_.items():
        primary.transitions_[offsetter(s)] = {
            t: set(map(offsetter, ds)) for t, ds in transitions.items()
        }
    
    # join secondary.accepts_ to primary[end]
    accept = offsetter(next(iter(secondary.accepts_)))
    if accept not in primary.transitions_:
        primary.transitions_[accept] = {}
    if NonCharTransition.EPSILON not in primary.transitions_[accept]:
        primary.transitions_[accept][NonCharTransition.EPSILON] = set()
    primary.transitions_[accept][NonCharTransition.EPSILON].add(end)
    
    return primary


def thompson(regex: str) -> Nfa:
    pass