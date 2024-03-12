from functools import reduce
import typing as t
from redfa.exception import MalformedRegexError

from redfa.nfa import Nfa
from redfa.token import tokenize, SpecialToken, Token
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
    for transition, dests in primary.transitions_.pop(accept, dict()).items():
        primary.transitions_[start][transition] = (
            primary.transitions_[start].get(transition, set()) | dests
        )
    for transitions in primary.transitions_.values():
        for dests in transitions.values():
            if accept in dests:
                dests.discard(accept)
                dests.add(start)
    
    # set secondary.accepts_ as primary.accepts_
    primary.accepts_ = set(map(offsetter, secondary.accepts_))
    
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


def _nothing() -> Nfa:
    return Nfa(
        states={0},
        transitions={},
        accepts={0},
        starts={1}
    )


class ThompsonParser(object):
    def __init__(self, tokenizer: t.Iterator[Token]) -> None:
        self.tokenizer = tokenizer
        self.current_token: Token | None = None
        self.token_used: bool = False
    
    def grab_if_used(self) -> bool:
        if self.token_used or self.current_token is None:
            try:
                self.current_token = next(self.tokenizer)
            except StopIteration:
                return False
            self.token_used = False
        return True
    
    def parse_char(self) -> Nfa | None:
        if not self.grab_if_used():
            return None
        if type(self.current_token) == str:
            self.token_used = True
            return _symbol_expression(self.current_token)
        return None
    
    def parse_round_bracket(self) -> Nfa | None:
        if not self.grab_if_used():
            return None
        # check if current expression starts with (
        if self.current_token != SpecialToken.OpenRoundBracket:
            return None
        self.token_used = True
        
        # list of expressions, expressions in a () can be separated by pipes '|'
        # which basically signify an "or" clause
        expressions: t.List[Nfa] = []
        pipe_encountered = True # pretend a pipe has been encountered
        while True:
            if not self.grab_if_used():
                raise MalformedRegexError("bracket expression is not closed")
            # when ) is encountered, exit the loop
            if self.current_token == SpecialToken.CloseRoundBracket:
                self.token_used = True
                break
            # when pipe is encountered, add a new expression
            elif self.current_token == SpecialToken.Pipe:
                self.token_used = True
                pipe_encountered = True
            # when a new expression is parsed, add to the current expression
            else:
                if not pipe_encountered:
                    raise MalformedRegexError("successive expression encountereed")
                expression = self.parse_expression()
                if expression is None:
                    raise MalformedRegexError("could not parse expression in bracket")
                expressions.append(expression)
        
        # join all the or clauses together
        return _union_expression(expressions)
    
    def parse_basic(self) -> Nfa | None:
        expression = self.parse_char()
        if expression is not None:
            return expression
        return self.parse_round_bracket()
    
    def parse_kleene(self) -> Nfa | None:
        expression = self.parse_basic()
        if expression is None:
            return None
        elif not self.grab_if_used(): # it's fine, just exit
            return expression
        if self.current_token == SpecialToken.Star:
            self.token_used = True
            return _kleene_star_expression(expression)
        elif self.current_token == SpecialToken.Plus:
            self.token_used = True
            return _kleene_plus_expression(expression)
        else:
            return expression
    
    def parse_expression(self) -> Nfa | None:
        expressions: t.List[Nfa] = []
        while True:
            expression = self.parse_kleene()
            if expression is None:
                break
            expressions.append(expression)
        if len(expressions) <= 0:
            return None
        big_one = expressions[0]
        for expression in expressions[1:]:
            big_one = _concatenate_nfa(big_one, expression)
        return big_one


def thompson(regex: str) -> Nfa | None:
    parser = ThompsonParser(tokenize(regex))
    nfa = parser.parse_expression()
    if nfa is None:
        return None
    return nfa.remove_deadends()