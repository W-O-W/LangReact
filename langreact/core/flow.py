from dataclasses import dataclass, field, replace
from enum import Enum
import re
from typing import List
from langreact.core.common.chunk import Chunk, new_none_chunk
from langreact.core.configure.configure import get_global_configure
from langreact.core.context import LocalContext, GlobalContext
from langreact.core.memory.memory import GlobalMemory
from langreact.core.params import InvokeParams
from langreact.core.plugin.plugins import (
    ApplicationPlugin,
    Plugin,
    ObserverPlugin,
    GlobalContextPlugin,
)
import logging
from langreact.core.constants import Events, Chunks
from langreact.core.plugin.qwen_plugin import QwenTurboPlugin
from langreact.core.steps import ConcludeStep, PlanStep
from langreact.core.tools import flatten_and_dropduplicate
import asyncio
from langreact.core.tools import get_timer
import logging
import copy


class Flow:
    def __init__(
        self,
        plugins: List[Plugin],
        configure_file: str = None,
        configure_class="Configure",
    ) -> None:
        """init Flow

        Args:
            plugins (List[Plugin]): all enable plugins

        Raises:
            RuntimeError: context init fail
            RuntimeError: plugins init fail
        """
        assert (
            len([plugin for plugin in plugins if isinstance(plugin, ApplicationPlugin)])
            > 0
        ), "at least one ApplicationPlugin"
        if configure_file is not None:
            self.configure = get_global_configure(configure_file, configure_class)
        else:
            self.configure = get_global_configure()
        if self.configure.DEFAULT_LLM_PLUGIN == "qwen-0.1":
            plugins.append(QwenTurboPlugin())

        self.context = GlobalContext(self.configure, plugins)
        # 初始化全局上下文和插件
        if not self.context.init():
            logging.error("[{}] init fail,please check log.".format(self.context))
            raise RuntimeError("[{}] init fail".format(self.context))
        logging.debug("init global context:{}".format(self.context))

        for plugin in plugins:
            if isinstance(plugin, GlobalContextPlugin):
                if plugin.init(global_context=self.context):
                    logging.debug("[{}] init success".format(plugin.name))
                    modifier = plugin.create_global_context_modifier()
                    if not modifier.invoke(self.context):
                        logging.error("[{}] invoke fail".format(plugin.name))
                    else:
                        logging.debug("[{}] invoke success".format(plugin.name))
                else:
                    logging.error(
                        "[{}] init fail,please check log.".format(plugin.name)
                    )
                    raise RuntimeError("[{}] init fail".format(plugin.name))
        logging.debug(
            "after global context plugins modifying,global context:{}".format(
                self.context
            )
        )
        for plugin in plugins:
            if not isinstance(plugin, GlobalContextPlugin):
                if plugin.init(global_context=self.context):
                    logging.debug("[{}] init success".format(plugin.name))
                else:
                    logging.error(
                        "[{}] init fail,please check log.".format(plugin.name)
                    )
                    raise RuntimeError("[{}] init fail".format(plugin.name))

        self.context.global_enable_plugins = plugins
        observers = flatten_and_dropduplicate(
            [
                plugin.create_observers(self.context)
                for plugin in plugins
                if isinstance(plugin, ObserverPlugin)
            ]
        )
        for observer in observers:
            self.context.observer_manager.register(observer)

        application_plugins = flatten_and_dropduplicate(
            [plugin for plugin in plugins if isinstance(plugin, ApplicationPlugin)]
        )
        self.context.application_map = {
            app_plugin.sign(): app_plugin for app_plugin in application_plugins
        }

    def prepare_context(
        self,
        user: str,
        origin_input_chunk: Chunk,
        params: InvokeParams,
        app_plugin: ApplicationPlugin,
    ) -> LocalContext:
        local_context = LocalContext(
            user,
            origin_input_chunk,
            application=app_plugin.create_new_application(self.context, self.configure),
            global_context=self.context,
            params=params,
        )
        assert local_context.init(), "local context init fail"
        input_chunk_modifier = app_plugin.create_input_chunk_modifier(
            local_context, origin_input_chunk
        )
        input_chunk = replace(origin_input_chunk)
        input_chunk_modifier.invoke(input_chunk)
        logging.info(
            "Origin input chunk:{}.After modified:{}".format(
                origin_input_chunk, input_chunk
            )
        )
        local_context.input_chunk = input_chunk
        app_plugin.create_local_context_modifier(params).invoke(local_context)
        local_context.application_plugin = app_plugin
        local_context.session.add_message(
            self.configure.ORIGIN_USER_INPUT_PROMPT.format(
                user=user, question=origin_input_chunk.data
            ),
            role="system",
        )

        if params.cot_web_retrieve or params.web_retrieve:
            local_context.search_application = (
                local_context.global_context.application_map[
                    params.search_application
                ].create_new_application(local_context,configure=self.configure)
            )
        return local_context

    async def invoke(
        self,
        user: str,
        origin_input_chunk: Chunk,
        params: InvokeParams,
    ):
        assert (
            params.application in self.context.application_map
        ), "application {} not enable".format(params.application)

        if params.web_retrieve or params.cot_web_retrieve:
            assert (
                params.search_application is not None
                and params.search_application in self.context.application_map
            ), "application {} not enable".format(params.application)

        application_plugin = self.context.application_map[params.application]
        local_context = self.prepare_context(
            user, origin_input_chunk, params, application_plugin
        )
        return_chunk = await self.__invoke__(local_context, local_context.params)
        output_builder = application_plugin.create_output_builder(local_context)
        output_builder.match_and_append(return_chunk)
        return output_builder.build()

    async def __invoke__(
        self,
        local_context: LocalContext,
        params: InvokeParams,
    ) -> Chunk:
        invoke_timer = get_timer()
        input_chunk = local_context.input_chunk
        local_context.params = params
        configure = self.configure
        # planning
        request_events = []
        response_chunks = []
        if params.cot:
            plan_step = PlanStep(local_context)
            request_events.extend(await plan_step.invoke(local_context, input_chunk))

        conclude_chunk = new_none_chunk()
        if len(request_events) > 0:
            response_chunks = self.notify_all_observers(
                local_context, input_chunk, request_events
            )

        if local_context.session.get_message_num(local_context.role) > 0:
            conclude_step = ConcludeStep()
            conclude_chunk = await conclude_step.invoke(
                local_context, input_chunk, *response_chunks
            )
            logging.info("current conclution:{}".format(conclude_chunk.data))
            question_text = configure.QUESTION_PROMPT.format(
                question=local_context.input_chunk.data
            )
            if local_context.session.invoke(question_text, role=local_context.role):
                response_chunk = Chunk(
                    command="LLM", data=local_context.session.messages[-1]["content"]
                )
                local_context.current_answer = response_chunk
            else:
                response_chunk = new_none_chunk()
        else:
            question_text = configure.QUESTION_WITHOUT_PROMPT.format(
                question=local_context.input_chunk.data
            )
            if local_context.session.invoke(question_text, role=local_context.role):
                response_chunk = Chunk(
                    command="LLM", data=local_context.session.messages[-1]["content"]
                )
                local_context.current_answer = response_chunk
            else:
                response_chunk = new_none_chunk()

        if params.reflection and params.max_step_num > local_context.current_step:
            local_context.current_step += 1
            reflection_context = self.reflection_context_prepare(local_context)
            if reflection_context is None:
                logging.info("skip reflection!")
                return_chunk = response_chunk
            else:
                return_chunk = self.__invoke__(
                    reflection_context, reflection_context.params
                )
        else:
            return_chunk = response_chunk
        logging.info(
            "invoke done.Total use time:{:.3f} s,input:{},output:{}".format(
                next(invoke_timer), input_chunk, return_chunk
            )
        )
        return return_chunk

    def reflection_context_prepare(
        self,
        context: LocalContext,
    ) -> LocalContext:
        configure = self.configure
        reflection_context = copy.copy(context)
        reflection_context.application = (
            context.application_plugin.create_new_application(context,configure, reflection=True)
        )

        if context.params.reflection_new_session:
            reflection_context.session = reflection_context.application.new_session(
                reflection_context,
                configure.REFLECTION_SYSTEM_CONTEXT.format(
                    role=reflection_context.role, user=reflection_context.user
                ),
            )
            reflection_question = configure.REFLECTION_QUESTION_PROMPT.format(
                question=reflection_context.input_chunk,
                actions=reflection_context.local_memory.to_natural_language(
                    configure.AVAILABLE_EVENTS_PROMPT
                ),
                current_answer=reflection_context.current_answer,
            )
            if reflection_context.session.invoke(
                reflection_question, role=reflection_context.role
            ):
                if re.match(
                    configure.REFLECTION_DETECT_REGEX,
                    reflection_context.session.messages[-1]["context"],
                ):
                    logging.info("begin reflection!")
                    return reflection_context
                else:
                    logging.info(
                        "reflection answer is 否:{}".format(
                            reflection_context.session.messages[-1]["context"]
                        )
                    )
        logging.info("skip reflection!")
        return None

    async def notify_all_observers(
        self, local_context: LocalContext, chunk: Chunk, events: List[Events]
    ) -> List[Chunk]:
        async_chunks = []
        events = flatten_and_dropduplicate(events)
        for event in events:
            accept_observers = [
                observer
                for observer in self.context.observer_manager.observers
                if observer.observe(event)
            ]
            if len(accept_observers) > 0:
                local_context.local_memory.append(event)
                async_chunks.append(
                    accept_observers[0].invoke(local_context, chunk)
                )  # TODO sort observer
            else:
                if local_context.params.tot_mode:
                    if local_context.params.tot_max_depth > 1:
                        tot_question = self.configure.TOT_QUESTION_PROMPT.format(
                            origin_question=local_context.input_chunk.data,
                            memory=local_context.local_memory.to_natural_language(
                                self.configure.AVAILABLE_EVENTS_PROMPT
                            ),
                            title=event.id,
                            description=event.description,
                        )
                        tot_context = copy.copy(local_context)
                        tot_context.input_chunk = Chunk(data=tot_question)
                        tot_params = copy.copy(local_context.params)
                        tot_params.tot_max_depth -= 1
                        async_chunks.append(
                            await self.__invoke__(tot_context, tot_params)
                        )

                question = self.configure.COT_QUESTION_DESCOMPOSITION_PROMPT.format(
                    question=local_context.input_chunk.data,
                    title=event.id,
                    description=event.description,
                )

                if local_context.session.invoke(question, role=local_context.role):
                    async_chunks.append(
                        Chunk(data=local_context.session.messages[-1]["context"])
                    )
                else:
                    async_chunks.append(new_none_chunk)

        if local_context.params.step_by_step:
            response_chunks = [await async_chunk for async_chunk in async_chunks]
        else:
            response_chunks = await asyncio.gather(*async_chunks)

        return flatten_and_dropduplicate(response_chunks)
