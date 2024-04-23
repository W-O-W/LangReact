from dataclasses import dataclass, field
import logging
from typing import List, Set
from langreact.core.common.chunk import Chunk
import abc


class OutputBuilder(abc.ABC):
    def match_and_append(self, append_chunk: Chunk) -> bool:
        return True

    @abc.abstractmethod
    def build(self) -> Chunk:
        """build return chunk"""

    def __repr__(self) -> str:
        return self.__class__.__name__


@dataclass
class DefaultOutputBuilder(OutputBuilder):
    accept_command: str
    chunks: List[Chunk] = field(default_factory=list, compare=False, init=False)

    def match_and_append(self, append_chunk: Chunk) -> bool:
        if append_chunk.command == self.accept_command:
            self.chunks.append(append_chunk)
            return True
        return False


    def build(self) -> Chunk:
        if len(self.chunks) > 0:
            return self.chunks[-1]
        else:
            logging.warn("output is empty.")
            return ""
