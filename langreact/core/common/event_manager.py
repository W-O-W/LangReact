from dataclasses import replace
from typing import List
from langreact.core.common.event import INVOKE_FINISH_EVENT, Event
from langreact.core.memory.memory import LocalMemory
from langreact.core.observer.observer_manager import ObserverManager
from langreact.core.tools import flatten_and_dropduplicate


class EventManager:
    def __init__(self) -> None:
        self.responsible_events = set([INVOKE_FINISH_EVENT])
        self.all_events = set([INVOKE_FINISH_EVENT])
        self.ob_manager: ObserverManager = None
        self.memory: LocalMemory = None

    def init(self, context):
        self.ob_manager = context.global_context.observer_manager
        self.memory = context.local_memory

    def __is_responsible_event__(self, event: Event):
        for observer in self.ob_manager.observers:
            if observer.observe(event):
                return True
        return False

    def is_responsible_event(self, event: Event, force_review=False):
        if force_review:
            return self.__is_responsible_event__(event)
        return event in self.responsible_events

    def register(self, *events):
        for event in events:
            self.all_events.add(event)
            if self.__is_responsible_event__(event):
                self.responsible_events.add(event)
                event.executable = True

    # TODO TOT
    def get_current_avaiable_events(self,remember_events_memory_size = 3) -> List[Event]:
        all_events = self.responsible_events
        memory_events = flatten_and_dropduplicate(
            self.memory.sequence[-remember_events_memory_size :]
        )
        memory_events = set(memory_events)
        return [
            event
            for event in all_events
            if event not in memory_events or not event.unique
        ]
