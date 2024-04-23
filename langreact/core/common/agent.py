from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
import logging
from typing import Union
from langreact.core.constants import Chunks, Events
import asyncio

from langreact.core.plugin.base import Plugin
from langreact.core.tools import get_timer



@dataclass(unsafe_hash=True)
class Agent(metaclass=ABCMeta):
    name: str
    producer_plugin: Plugin = field(default=None)

    @abstractmethod
    async def __invoke__(
        self, context, chunks: Chunks
    ) -> Union[Events, Chunks]:
        """agent invoke function.
        In LangReact,Chunks is input of Agent,Agent reads chunk and analyse it,
        then based on plugins transfer chunk to events or other chunks.
        """

    #TODO add memory
    async def invoke(
        self, context, chunks: Chunks
    ) -> Union[Events, Chunks]:
        task = asyncio.create_task(self.__invoke__(context, chunks))
        def __handle__(task):
            pass
            
        task.add_done_callback(__handle__)
        return await task

    def sign(self, with_version=True) -> str:
        if with_version:
            return "Agent {agent} generated from  Plugin[{plugin}-{version}]".format(
                agent=self.name.capitalize(),
                plugin=self.producer_plugin.name.capitalize(),
                version=self.producer_plugin.version,
            )
        else:
            return "Agent {agent} generated from  Plugin[{plugin}]".format(
                agent=self.name.capitalize(),
                plugin=self.producer_plugin.name.capitalize(),
            )
