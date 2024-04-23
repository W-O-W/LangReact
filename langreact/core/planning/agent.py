from dataclasses import dataclass, field
from typing import Any, List, Type, Callable
from langreact.core.common.chunk import Chunk
from langreact.core.common.event import NONE_EVENT, Event
from langreact.core.tools import flatten_and_dropduplicate


@dataclass
class PlanningAgent:
    name: str
    return_events: List[Event]
    dynamic:bool = field(default=False,compare=False)

    def is_available(self) -> bool:
        return True

    async def map(self, chunk: Chunk, context) -> List[Event]:
        return self.return_events


def PlanningAgentWrapper(*return_events, T: Type[PlanningAgent] = PlanningAgent, **kwargs):
    class PlanningAgentTmp(T):
        def __init__(self, func: Callable[[T, Chunk, Any], Event]) -> None:
            T.__init__(self,T.__name__, return_events)
            self._map = func
            for k, v in kwargs.items():
                self.__setattr__(k, v)

        def is_available(self) -> bool:
            return True

        async def map(self, chunk: Chunk, context) -> List[Event]:
            events = self._map(self, chunk, context)
            if events == None:
                events = NONE_EVENT
            events = flatten_and_dropduplicate(events)
            for event in events:
                if event != NONE_EVENT:
                    assert event in self.return_events, "{} not in {}".format(
                        event, self.return_events
                    )
            return events
    return PlanningAgentTmp
