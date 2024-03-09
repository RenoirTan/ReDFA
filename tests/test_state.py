from redfa.state import State, AcceptState
from redfa.transition import Transition, NonCharTransition


def test_simple_ab_state():
    start = State()
    a = State()
    b = AcceptState()
    a.add_transition("b", b)
    start.add_transition("a", a)
    
    assert start.transition(NonCharTransition.START) is start
    assert start.transition("a") is a
    assert a.transition("b") is b
    assert a.transition("a") is None
    assert b.transition("b") is None
    assert b.transition(NonCharTransition.END) is b
    assert b.can_end_here()