from langreact.core.common.chunk import Chunk
from langreact.core.common.feedback_chunk import FeedbackChunk
from langreact.core.context import LocalContext

from langreact.core.observer.observer import Observer

class FeedBackObserver(Observer):
    async def __invoke__(
        self, context: LocalContext, feedback_chunk: FeedbackChunk
    ) -> Chunk:
        chunks = context.global_context.memory.get(
            filter=lambda chunk: chunk.end_chunk == feedback_chunk.feedback_chunk
        )
        for chunk in chunks:
            chunk.feedback = feedback_chunk
        return Chunk(
            command="RETURN",
            data="thank you for your feedback,we will deal with it as soon as possible.",
        )


# @dataclass
# class WithFeedbackPlugin(PlanningAgentPlugin, ObserverPlugin):
#     feedback_event: Event
#     feedback_mappings: List[PlanningAgent]
#     feedback_observer: FeedBackObserver

#     def init(self, context: GlobalContext) -> bool:
#         self.__react_event__ = Event(
#             self.feedback_event.id
#             + global_basic_config.DEFAULT_EVENT_SCOPE_SEP
#             + "feedback"
#         )
#         for mapping in self.feedback_mappings:
#             mapping.return_events = self.__react_event__
#         self.feedback_observer.observe = lambda event: self.__react_event__ == event
#         return True

#     def create_observers(self, context: GlobalContext) -> List[Observer]:
#         return [
#             self.feedback_observer,
#         ]

#     def create_event_mappings(self, context: GlobalContext) -> List[PlanningAgent]:
#         return self.feedback_mappings
