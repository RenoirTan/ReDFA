from functools import reduce
import typing as t
from redfa.exception import MalformedRegexError

from redfa.nfa import Nfa
from redfa.token import tokenize, SpecialToken, Token
from redfa.transition import NonCharTransition, Transition


__all__ = ["ThompsonParser", "thompson"]


def _empty_expression() -> Nfa:
    """
    Create an NFA with one epsilon transition from 0 to 1, with 0 being the
    start and 1 being an accept state. This expression is particularly useful
    for building an expression with an optional skip.
    """
    return Nfa(
        states={0, 1},
        transitions={0: {NonCharTransition.EPSILON: {1}}},
        accepts={1},
        starts={0},
        groups=[]
    )


def _symbol_expression(char: Transition) -> Nfa:
    """
    Create an NFA where `char` is a transition from state 0 to state 1.
    """
    return Nfa(
        states={0, 1},
        transitions={0: {char: {1}}},
        accepts={1},
        starts={0},
        groups=[]
    )


def _kleene_plus_expression(expression: Nfa) -> Nfa:
    """
    Convert `expression` into a kleene plus expression.
    """
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
    """
    Convert `expression` into a kleene star expression.
    """
    return _optional_expression(_kleene_plus_expression(expression))


def _optional_expression(expression: Nfa) -> Nfa:
    """
    Convert `expression` into an optional expression.
    """
    return _join_nfa(_empty_expression(), expression, 0, 1)


def _union_expression(expressions: t.Iterable[Nfa]) -> Nfa:
    """
    Create a "branched" expression from `expressions`.
    """
    primary = Nfa(
        states={0, 1},
        transitions={},
        accepts={1},
        starts={0},
        groups=[]
    )
    for expression in expressions:
        _join_nfa(primary, expression, 0, 1)
    return primary


def _grouped_expression(expression: Nfa) -> Nfa:
    """
    Make this expression grouped. Assumes one start and one accept.
    """
    start = next(iter(expression.starts_))
    accept = next(iter(expression.accepts_))
    if (start, accept) not in expression.groups_:
        expression.groups_.insert(0, (start, accept))
    return expression


def _concatenate_nfa(primary: Nfa, secondary: Nfa) -> Nfa:
    """
    Add secondary to primary, such that the starting state of secondary becomes
    the accepting state of primary. This function requires that primary and
    secondary each have only one accept state and one start state.
    """
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
    
    # link primary.accepts_ to secondary.starts_
    start = offsetter(next(iter(secondary.starts_)))
    accept = next(iter(primary.accepts_))
    if accept not in primary.transitions_:
        primary.transitions_[accept] = {}
    if NonCharTransition.EPSILON not in primary.transitions_[accept]:
        primary.transitions_[accept][NonCharTransition.EPSILON] = set()
    primary.transitions_[accept][NonCharTransition.EPSILON].add(start)
    """
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
    """
    
    # set secondary.accepts_ as primary.accepts_
    primary.accepts_ = set(map(offsetter, secondary.accepts_))
    
    # add groups from secondary to primary
    primary.groups_.extend(((offsetter(s), offsetter(a)) for s, a in secondary.groups_))
    
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
    
    # add groups from secondary to primary
    primary.groups_.extend(((offsetter(s), offsetter(a)) for s, a in secondary.groups_))
    
    return primary


def _nothing() -> Nfa:
    """
    Create an empty expression.
    """
    return Nfa(
        states={0},
        transitions={},
        accepts={0},
        starts={0},
        groups=[]
    )


class ThompsonParser(object):
    def __init__(self, tokenizer: t.Iterator[Token]) -> None:
        self.tokenizer = tokenizer
        self.current_token: Token | None = None
        self.token_used: bool = False
    
    def grab_if_used(self) -> bool:
        """
        Grab a token from the tokeniser, if the token has already been used
        during one of the parsing steps. If successful, this function returns
        True and guarantees that the current token has not been used before. If
        it fails, False is returned.
        """
        if self.token_used or self.current_token is None:
            try:
                self.current_token = next(self.tokenizer)
            except StopIteration:
                return False
            self.token_used = False
        return True
    
    def parse_char(self) -> Nfa | None:
        """
        Parse character.
        """
        if not self.grab_if_used():
            return None
        if type(self.current_token) == str:
            self.token_used = True
            return _symbol_expression(self.current_token)
        return None
    
    def parse_round_bracket(self) -> Nfa | None:
        """
        Parse round bracket expressions, including those with pipes in them.
        """
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
        return _grouped_expression(_union_expression(expressions))
    
    def parse_basic(self) -> Nfa | None:
        """
        Parse "atomic" expressions, like characters and brackets.
        """
        expression = self.parse_char()
        if expression is not None:
            return expression
        return self.parse_round_bracket()
    
    def parse_kleene(self) -> Nfa | None:
        """
        Add additional data onto an expression.
        """
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
        elif self.current_token == SpecialToken.Question:
            self.token_used = True
            return _optional_expression(expression)
        else:
            return expression
    
    def parse_expression(self) -> Nfa | None:
        """
        Parse one expression.
        """
        expressions: t.List[Nfa] = []
        while True:
            expression = self.parse_kleene()
            if expression is None:
                break
            expressions.append(expression)
        if len(expressions) <= 0:
            return None
        return reduce(_concatenate_nfa, expressions)


def thompson(regex: str) -> Nfa | None:
    """
    Create an NFA using Thompson's Construction. Returns None if nothing is
    parsed.
    """
    parser = ThompsonParser(tokenize(regex))
    nfa = parser.parse_expression()
    if nfa is None:
        return None
    return nfa.remove_deadends()