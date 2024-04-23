
import asyncio
from langreact.core.observer.observer import *
import pytest
@pytest.mark.dependency(name="a")
def test_observer():
    @ObserverWrapper(Event("A","do"))
    async def observerA(self, context, chunks: Chunks) -> Chunks:
        return chunks
    
    @ObserverWrapper(Event("B","do"))
    async def observerB(self, context, chunks: Chunks) -> Chunks:
        return chunks
    
    e = Event("A","do")
    assert observerA.observe(e)

    async def run():
        return [await observerA.__invoke__(None,e), await observerB.__invoke__(None,e)]
    
    print(asyncio.run(run()))