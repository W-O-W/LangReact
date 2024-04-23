from dataclasses import MISSING, dataclass, field
import logging
from typing import List, Mapping

from langreact.core.configure.default import Configure
from langreact.core.application import Application, Session
from langreact.core.common.chunk import Chunk, new_none_chunk
from langreact.core.common.event_manager import EventManager
from langreact.core.memory.memory import GlobalMemory, LocalMemory
from langreact.core.observer.observer_manager import ObserverManager
from langreact.core.params import InvokeParams
from langreact.core.plugin.plugins import ApplicationPlugin


@dataclass
class GlobalContext:
    configure:Configure = field(default = MISSING)
    global_enable_plugins: List = field(default_factory=list)
    application_map: Mapping[str, ApplicationPlugin] = field(default_factory=dict)
    MAX_CHUNK_WAIT_TIME: int = 100
    memory: GlobalMemory = field(default_factory=GlobalMemory)
    observer_manager: ObserverManager = field(default_factory=ObserverManager)

    def init(self) -> bool:
        return self.memory.init(self.configure)


@dataclass
class LocalContext:
    user: str
    origin_input_chunk: Chunk = field(default=MISSING)
    global_context: GlobalContext = field(default=MISSING)
    params: InvokeParams = field(default=MISSING)
    application: Application = field(default=None)
    search_application: Application = field(default=None)  # TODO search from google
    input_chunk: Chunk = field(default_factory=new_none_chunk)
    application_plugin: ApplicationPlugin = field(default=None)
    local_memory: LocalMemory = field(default=None)
    event_manager: EventManager = field(default_factory=EventManager)
    current_answer: Chunk = field(default_factory=new_none_chunk)

    role: str = field(default="user")
    current_step: int = field(default=0)

    session: Session = field(default=None)
    plan_session: Session = field(default=None)

    def init(self) -> bool:
        self.event_manager.init(self)
        self.local_memory = LocalMemory(user=self.user)
        self.session = self.application.new_session(
            self,
            self.application.configure.MAIN_SYSTEM_PREFIX_PROMPT.format(
                role=self.role, user=self.user
            ),
        )
        if not self.params.cot_new_session:
            self.plan_session = self.session
        return True
