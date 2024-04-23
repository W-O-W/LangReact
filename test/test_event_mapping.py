import asyncio

from langreact.core.common.chunk import Chunk
from langreact.core.common.event import Event
from langreact.core.context import GlobalContext, LocalContext
from langreact.core.params import InvokeParams
from langreact.core.planning.agent import PlanningAgent, PlanningAgentWrapper


class T1(PlanningAgent):
    pass


def test_event_mapping_wrapper():
    @PlanningAgentWrapper(Event(id="A", description="do"), T=T1)
    def map_test(self, chunk: Chunk, context: LocalContext) -> Event:
        return Event(id="A", description="a")

    assert map_test.is_available()
    assert map_test.name == "T1"

    e = asyncio.run(
        map_test.map(
            Chunk(),
            LocalContext(
                "test",
                Chunk(),
                global_context=GlobalContext([]),
                params=InvokeParams(application="test"),
            ),
        )
    )
    assert e[0].id == "A"


if __name__ == "__main__":
    test_event_mapping_wrapper()
