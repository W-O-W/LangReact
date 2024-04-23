
from dataclasses import dataclass, field
from typing import List

from langreact.core.observer.observer import Observer


@dataclass
class ObserverManager:
    observers: List[Observer] = field(default_factory=list)

    def register(self, observer):
        self.observers.append(observer)
