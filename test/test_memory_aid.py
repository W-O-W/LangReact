
import asyncio
from langreact.core.common.chunk import Chunk
from langreact.core.context import GlobalContext, LocalContext
from langreact.core.common.event import Event


def test_memory_aid(setup):
    pass
    # test = MemoryAidPlanningAgent("test",[])
    # g_context = GlobalContext()
    # g_context.init()
    # context = LocalContext("test",input_chunk=Chunk(command = "QA",data="老子是否是道教创始人?"),global_context=g_context)
    # context.init()
    # context.local_memory.append(context.input_chunk)
    # print(asyncio.run(test.map(context.input_chunk,context)))
