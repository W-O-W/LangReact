"""
File Created: Wednesday, 28th February 2024 6:25:50 pm
Author: zhangli.max (zhangli.max@bigo.com)
-----
Last Modified: Wednesday, 28th February 2024 7:52:58 pm
Modified By: zhangli.max (zhangli.max@bigo.com)
"""

from chunk import Chunk


class DataNode:
    def new_chunk(self) -> Chunk:
        assert self.alive(), "died"
        return self.register_new_chunk()

    def next_filled_chunk(self) -> Chunk:
        return next(self.buffer)

    def alive(self) -> bool:
        pass

    def register_new_chunk(self) -> Chunk:
        new_chunk = Chunk()
        self.buffer.push(new_chunk)
        return new_chunk
    
    