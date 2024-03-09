import typing as t

from redfa.transition import Transition, NonCharTransition


class State(object):
    def __init__(self, edges: t.Dict[Transition, "State"] | None = None) -> None:
        self.edges = edges if edges is not None else {}
    
    def add_transition(self, transition: Transition, dest: "State") -> None:
        self.edges[transition] = dest
    
    def transition(self, transition: Transition) -> "State | None":
        # If is ^ or $, go to self if no destination
        default_out = self if isinstance(transition, NonCharTransition) else None
        return self.edges.get(transition, default_out)
    
    def can_end_here(self) -> bool:
        return False
    

class AcceptState(State):
    def can_end_here(self) -> bool:
        return True