

from langreact.core.common.chunk import Chunk


def test_chunk():
    chunk = Chunk()
    chunk.data = "T1"
    print(chunk)
