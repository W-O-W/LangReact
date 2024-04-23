from dataclasses import MISSING
from typing import Callable, List, Union

from langreact.core.common.chunk import Chunk, new_none_chunk
from langreact.core.constants import Chunks, Events
from langreact.core.common.event import Event
from langreact.core.memory.memory_chunk import GlobalMemoryChunk
from langreact.core.memory.memory_index import MemoryIndex
from langreact.core.tools import flatten_and_dropduplicate


class GlobalMemory:
    """每一个 flow 的全局 memory 记录：
    1. Flow 一次 invoke 的输入和输出 chunk
    2. 每一个中间的 event 信号
    3. 用户对一次 invoke 的 feedback
    """

    def __init__(self) -> None:
        self.memory_chunks: List[GlobalMemoryChunk] = []
        self.memory_chunk_index = None

    def init(self, configure) -> bool:
        self.memory_chunk_index = MemoryIndex(configure)
        return self.memory_chunk_index.alive()

    def append(self, memory_chunk: GlobalMemoryChunk):
        self.memory_chunks.append(memory_chunk)
        if self.memory_chunk_index.alive():
            status = self.memory_chunk_index.insert(memory_chunk)
            assert status["insert_count"] == 1, "insert memory fail"
            memory_chunk.data = {"id": status["ids"][0]}

    def get(
        self, idx=None, filter: Callable[[GlobalMemoryChunk], bool] = None
    ) -> List[GlobalMemoryChunk]:
        assert idx is None and filter is None, "get memory by idx or filter"
        if idx is not None:
            return [self.memory_chunks[idx]]
        return [memory for memory in self.memory_chunks if filter(memory)]


class LocalMemory:
    """每次 invoke 本地 memory 记录：
    [Event1,[Sub Event1,SubEvent2],Event2]
    1.Event1
        a.SubEvent1
        b.SubEvent2
    2.Event2
    """

    def __init__(self, user) -> None:
        self.user = user
        self.sequence: List = []

    def append(self, elements: Events, index: List[int] = []):
        current_sequence = self.sequence
        for idx in index:
            current_sequence = current_sequence[idx]
        current_sequence.append(elements)

    def new_event(self, **kwargs):
        e = Event(**kwargs)
        self.append(e)
        return e

    def to_global_memory_chunk(self, input_chunk, end_chunk=None):
        memory_chunk = GlobalMemoryChunk(user=self.user)
        memory_chunk.begining_chunk = input_chunk
        if end_chunk != None:
            memory_chunk.end_chunk = end_chunk
        else:
            memory_chunk.end_chunk = new_none_chunk()
        memory_chunk.react_events = self.sequence
        return memory_chunk

    def __to_natural_language__(self, events_prompt, sequence):
        texts = []
        idx = 1
        for e in sequence:
            if isinstance(e, list):
                texts.append("\t" + self.__to_natural_language__(e))
            else:
                texts.append(
                    events_prompt.format(num=idx, event=e.to_natural_language())
                )
                idx += 1
        return "\n".join(texts)

    def to_natural_language(self, events_prompt):
        return self.__to_natural_language__(events_prompt, self.sequence)
