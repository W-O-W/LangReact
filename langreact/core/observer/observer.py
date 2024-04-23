from langreact.core.common.agent import Agent
from langreact.core.common.chunk import new_none_chunk
from langreact.core.common.event import Event
from typing import Any, Type, Callable
from langreact.core.constants import Chunks


class Observer(Agent):
    def observe(self, event: Event) -> bool:
        return False

    async def __invoke__(self, context, chunks: Chunks) -> Chunks:
        return new_none_chunk()


def ObserverWrapper(event: Event, T: Type = Observer, **kwargs):
    class ObserverTmp(T):
        def __init__(self, func: Callable[[T, Any, Chunks], Chunks]) -> None:
            T.__init__(self, T.__name__)
            self._invoke = func
            self._event = event
            for k, v in kwargs.items():
                self.__setattr__(k, v)

        async def __invoke__(self, context, chunks: Chunks) -> Chunks:
            return self._invoke(self, context, chunks)

        def observe(self, event: Event) -> bool:
            return self._event == event

    return ObserverTmp
