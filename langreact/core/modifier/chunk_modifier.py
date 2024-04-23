from typing import Callable, List, Type
from langreact.core.common.chunk import Chunk
from dataclasses import replace,asdict

class ChunkModifier:
    def invoke(self, chunk: Chunk, fix_chunks: List[Chunk] = []) -> List[Chunk]:
        """modify one Chunk by fix_chunks

        Args:
            chunk (Chunk): original chunk
            fix_chunks (List[Chunk], optional): modify original chunk by them. Defaults to [].

        Returns:
            Chunk: modified chunk
        """
        if len(fix_chunks) > 0:
            for fix_chunk in fix_chunks:
                for key, value in asdict(fix_chunk).items():
                    setattr(chunk, key, value)
            return []
        return fix_chunks
    def __repr__(self) -> str:
        return self.__class__.__name__

def ChunkModifierWrapper(T: Type = ChunkModifier, **kwargs):
    """Wrapper of ChunkModifier

    Args:
        T (Type, optional): base class of ChunkModifier. Defaults to ChunkModifier.

    Returns:
        ContextModifierTmp: a singleton of T
    """
    class ContextModifierTmp(T):
        def __init__(self, func: Callable[[T, Chunk, List[Chunk]],List[Chunk]]) -> None:
            T.__init__(self)
            self._invoke = func
            for k, v in kwargs.items():
                self.__setattr__(k, v)

        def invoke(self, chunk: Chunk, fix_chunks: List[Chunk]) -> List[Chunk]:
            return self._invoke(self, chunk, fix_chunks)
        
        def __repr__(self) -> str:
            return T.__name__

    return ContextModifierTmp
