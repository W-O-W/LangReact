"""

[SCOPE][COMMAND][DATA][SEP]
"""

from dataclasses import dataclass, field
from typing import Any, TypeVar, List

DataType = TypeVar("DataType", str, List[str])


@dataclass(unsafe_hash=True)
class Chunk:
    command: str = ""
    data: DataType = field(default_factory=str)

    def from_json(json_chunk):
        chunk = Chunk()
        for k, v in json_chunk.items():
            setattr(chunk, k, v)
        return chunk

    def to_natural_language(self):
        return str(self.data)


def new_none_chunk():
    return Chunk("NOTHING", "")

NONE_CHUNK=new_none_chunk()

# @dataclass(unsafe_hash=True)
# class AsyncChunk(Chunk):
#     def set_task(self, async_task: asyncio.Task) -> None:
#         async_task.add_done_callback(lambda x:self.init_from(x.result()))
#         self.__async_task__ = async_task

#     def init_from(self, chunk: Chunk):
#         self.command = chunk.command
#         self.scope = chunk.scope
#         self.data = chunk.data
