from typing import Any, List
from dataclasses import MISSING, dataclass, field

from langreact.core.plugin.base import Plugin


@dataclass(unsafe_hash=True)
class Event:
    id: str
    description: str = field(compare=False, hash=False)
    producer: str = field(default="", compare=False)
    record: bool = field(default=True, compare=False, hash=False)
    prefer_score: float = field(default=0, compare=False, hash=False)
    unique:bool = field(default=True, compare=False, hash=False)
    executable:bool = field(default=False, compare=False, hash=False)

    def to_natural_language(self):
        return self.id

    def from_json(json_event):
        e = Event("", "")
        for k, v in json_event.items():
            setattr(e, k, v)
        return e

NONE_EVENT = Event(
    "#NONE#",
    description="do nothing.",
    record=False,
)
INVOKE_FINISH_EVENT = Event(
    "结束对话", description="返回当前结果.", record=False
)