import asyncio
import copy
from dataclasses import replace
from enum import Enum
import logging
from typing import List

from langreact.core.common.agent import Agent
from langreact.core.common.chunk import NONE_CHUNK, Chunk, new_none_chunk
from langreact.core.common.event import Event
from langreact.core.context import LocalContext
from langreact.core.planning.agent import PlanningAgent
from langreact.core.plugin.plugins import (
    PlanningAgentPlugin,
)
from langreact.core.tools import get_timer, is_sub_match


class PlanStep(Agent):
    def __init__(self, context: LocalContext) -> None:
        """init PlanningAgent

        Args:
            context (GlobalContext): global context
            plugins (List[PlanningAgentPlugin]): plugins of PlanningAgentPlugin
        """
        self.planning_agents: List[PlanningAgent] = []

        pa_plugins = [
            plugin
            for plugin in context.global_context.global_enable_plugins
            if isinstance(plugin, PlanningAgentPlugin)
        ]
        logging.info(
            "{num} planning agents enable:{plugins}".format(
                num=len(pa_plugins), plugins=[plugin.sign() for plugin in pa_plugins]
            )
        )

        for plugin in pa_plugins:
            for agent in plugin.create_planning_agents(context):
                context.event_manager.register(*agent.return_events)
                self.planning_agents.append(agent)
                logging.info("plugin {} registers success".format(plugin))

        super().__init__("PLAN_STEP")

    async def __invoke__(
        self, context: LocalContext, input_chunk: Chunk
    ) -> List[Event]:
        timer = get_timer()
        configure = context.application.configure
        plan_context = copy.copy(context)
        params = copy.copy(plan_context.params)
        plan_context.params = params
        plan_context.current_answer = new_none_chunk()
        session = plan_context.plan_session
        plan_context.role = params.plan_role
        if session is None:
            # 一次 cot 只允许一个 session
            plan_context.plan_session = plan_context.application.new_session(
                plan_context,
                configure.PLAN_STEP_SYSTEM_CONTEXT_PROMPT.format(
                    role=plan_context.role, user=plan_context.user
                ),
            )
            session = plan_context.plan_session

        if context.current_answer != NONE_CHUNK:
            msg = configure.PLAN_STEP_REFINE_ANSWER_PROMPT.format(
                question=plan_context.input_chunk.data,
                current_answer=plan_context.current_answer.data,
            )
            session.add_message(msg, plan_context.role)

        if params.cot_web_retrieve:
            web_seach_engine = (
                params.search_application.new_session(
                    plan_context, configure.WEB_SEARCH_ENGINE_SYETEM_CONTEXT
                )
            )
            web_retrive_result = web_seach_engine.invoke(
                configure.SEARCH_WEB_PROMPT.format(
                    query=input_chunk.to_natural_language(),
                    num=params.web_reference_num,
                ),
                enable_search=True,
            )

            session.add_message(
                configure.WEB_SEARCH_PREFIX_CONTEXT + web_retrive_result,
                plan_context.role,
            )
            session.add_message(configure.WEB_SEARCH_QUESTION, role=plan_context.role)

        if params.cot_memory_aid:
            # TODO memory structure
            memory_list = plan_context.global_context.memory.memory_chunk_index.search_from_scentences(
                input_chunk.to_natural_language(),
                limit=configure.MEMORY_AID_SIZE,
            )
            session.add_message(
                configure.MEMORY_PREFIX_CONTEXT
                + "\n".join([memory for memory in memory_list[0]]),
                plan_context.role,
            )
            session.add_message(configure.MEMORY_CONCLUTION_QUESTION, role=plan_context.role)
            # TODO Memory Feedback

        conclude_chunk = new_none_chunk()
        if params.cot_conclude and not params.cot_new_session:
            params.web_retrieve = False
            params.memory_retrieve = False
            conclude_step = ConcludeStep(plan_context)
            conclude_chunk = await conclude_step.invoke(plan_context)
            logging.info("Planing Conclution:{}".format(conclude_chunk.data))

        # avaiable_events: List[Event] = (
        #     context.event_manager.get_current_avaiable_events(context.local_memory)
        # )
        # if len(avaiable_events) > 0:
        #     session.add_message(
        #         configure.TOOL_USE_PREFIX_CONTEXT
        #         + "\n".join(
        #             [
        #                 configure.TOOL_PROMPT.format(
        #                     num=idx, title=event.id, description=event.description
        #                 )
        #                 for idx, event in enumerate(avaiable_events)
        #             ]
        #         ),
        #         plan_context.role,
        #     )
        #     session.add_message(configure.TOOL_USE_QUESTION, role=plan_context.role)

        if params.step_by_step and params.step_adjust_planning:
            question_text = configure.COT_ADJUST_PLANNING_QUESTION_PROMPT.format(
                memory=plan_context.local_memory.to_natural_language(configure.AVAILABLE_EVENTS_PROMPT)
            )
        else:
            question_text = configure.COT_QUESTION_DESCOMPOSITION_PROMPT.format(
                max_step=params.cot_max_step_num,
                memory=plan_context.local_memory.to_natural_language(configure.AVAILABLE_EVENTS_PROMPT),
                question=input_chunk.data,
            )
        llm_answer = Chunk("LLM")
        selected_events = []
        if session.invoke(question_text, role=plan_context.role):
            llm_answer.data = session.messages[-1]["content"]

        plan_context.current_answer = llm_answer
        for idx, title, desc in configure.PLAN_STEP_REGEX.findall(llm_answer.data):
            selected_events.append(Event(title, description=desc, prefer_score=1 / float(idx)))

        # TODO support ART by PlanningAgentPlugin and Observers

        if params.cot_reflection:
            # only one time
            params.cot_reflection = False
            return await self.__invoke__(plan_context, input_chunk)

        return selected_events


class ConcludeStep(Agent):
    def __init__(self):
        super().__init__("CONCLUDE_STEP")
    async def __invoke__(self, context: LocalContext, input_chunk: Chunk) -> Chunk:
        conclude_context = copy.copy(context)
        configure = conclude_context.application.configure
        params = conclude_context.params
        session = conclude_context.session

        if params.cot_web_retrieve:
            web_seach_engine = (
                params.search_application.new_session(
                    conclude_context, configure.WEB_SEARCH_ENGINE_SYETEM_CONTEXT
                )
            )
            web_retrive_result = web_seach_engine.invoke(
                configure.SEARCH_WEB_PROMPT.format(
                    query=input_chunk.to_natural_language(),
                    num=params.web_reference_num,
                ),
                enable_search=True,
            )

            session.add_message(
                configure.WEB_SEARCH_PREFIX_CONTEXT + web_retrive_result,
                conclude_context.role,
            )
            session.add_message(
                configure.WEB_SEARCH_QUESTION, role=conclude_context.role
            )

        if params.cot_memory_aid:
            # TODO memory structure
            memory_list = conclude_context.global_context.memory.memory_chunk_index.search_from_scentences(
                input_chunk.to_natural_language(),
                limit=configure.MEMORY_AID_SIZE,
            )
            memory_list = memory_list[0]
            if len(memory_list) > 0:
                session.add_message(
                    configure.MEMORY_PREFIX_CONTEXT
                    + "\n".join([memory for memory in memory_list]),
                    conclude_context.role,
                )
                session.add_message(configure.MEMORY_CONCLUTION_QUESTION, role=conclude_context.role)
            # TODO Memory Feedback

        if session.invoke(
            configure.CONCLUDE_REFINE_QUESTION, role=conclude_context.role
        ):
            return Chunk(data=session.messages[-1]["content"])
        else:
            return new_none_chunk()

    def __repr__(self) -> str:
        return self.__class__.__name__
