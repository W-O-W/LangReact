from dataclasses import MISSING, dataclass, field, asdict, replace
from datetime import datetime
from typing import List
from langreact.core.configure.configure import get_global_configure
from langreact.core.application import Application
from langreact.core.common.chunk import Chunk, new_none_chunk
from langreact.core.common.feedback_chunk import FeedbackChunk
from langreact.core.constants import Events
from langreact.core.common.event import Event
from langreact.core.plugin.plugins import ApplicationPlugin
from langreact.core.tools import clean_default_values


@dataclass
class GlobalMemoryChunk(Chunk):
    user: str = ""
    begining_chunk: Chunk = field(default=None)
    end_chunk: Chunk = field(default=None)
    react_events: List[List[Events]] = field(default_factory=list)
    feedback: FeedbackChunk = field(default=None)
    happen_time: datetime = field(default_factory=datetime.now)
    application: ApplicationPlugin = field(default=None)

    def to_json(self):
        dict_data = asdict(self)
        dict_data["happen_time"] = self.happen_time.timestamp()
        dict_data["user"] = None
        return clean_default_values(dict_data)

    def from_json(user, json_chunk):
        chunk = GlobalMemoryChunk(user=user)
        for k, v in json_chunk.items():
            if k == "user":
                continue

            if k == "begining_chunk" or k == "end_chunk":
                v = Chunk.from_json(v)
            elif k == "feedback":
                v = FeedbackChunk.from_json(v)
            elif k == "react_events":
                react_events = []
                for elist in v:
                    react_events.append([])
                    for events in elist:
                        if isinstance(events, list):
                            react_events[-1].append(
                                [Event.from_json(event_dict) for event_dict in events]
                            )
                        else:
                            react_events[-1].append(Event.from_json(events))
                v = react_events
            elif k == "happen_time":
                v = datetime.fromtimestamp(v)
            elif k == "application":
                v = ApplicationPlugin()
            setattr(chunk, k, v)
        return chunk

    def to_natural_language(self,configure = get_global_configure(), with_end=True):
        begining_chunk = self.begining_chunk.to_natural_language().strip(".")
        end_chunk = self.end_chunk.to_natural_language().strip(".")
        if self.feedback is None:
            feedback = ""
        else:
            feedback = self.feedback.to_natural_language().strip(".")
        events_str_list = []
        happen_time = datetime.strftime(self.happen_time, "%Y-%m-%d %H点")
        if len(self.react_events) > 1:
            for phase, events in enumerate(self.react_events):
                if len(events) == 0:
                    events_str = "在第 {phase} 个阶段,我什么也没执行\n".format(
                        phase=phase
                    )
                else:
                    events_str = "在第 {phase} 个阶段,我执行了 {nums} 个步骤:\n".format(
                        phase=phase, nums=len(events)
                    )
                    for idx, event in enumerate(events):
                        events_str += (
                            "{}. {}.".format(
                                idx + 1, event.to_natural_language().strip(".")
                            )
                            + "\n"
                        )
                events_str_list.append(events_str.strip())
            events_str = "我分了 {nstep} 个阶段来寻找答案:\n".format(
                nstep=len(self.react_events)
            ) + "\n".join(events_str_list)
        elif len(self.react_events) == 1:
            events_str = "为了找到答案，我执行了 {nums} 个步骤:\n".format(
                phase=phase, nums=len(events)
            )
            for idx, event in enumerate(events):
                events_str += (
                    "{}. {}.".format(idx, event.to_natural_language().strip(".")) + "\n"
                )
        else:
            events_str = ""
        # TODO prompt management
        return (
            configure.MEMORY_PROMPT.format(
                time=happen_time,
                question=begining_chunk,
                events=events_str,
                answer=end_chunk if with_end else "",
                feedback=feedback,
            )
            .replace("..", ".")
            .strip()
        )
