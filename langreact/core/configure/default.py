from dataclasses import dataclass, field
import re
from typing import List
from langchain.prompts import PromptTemplate
import os


@dataclass
class Configure:

    # application 配置
    DEFAULT_ROLE = "user"
    DEFAULT_LLM_PLUGIN = "qwen-0.1"
    DEFAULT_LLM_RETRY_NUM = 2



    MAIN_SYSTEM_PREFIX_PROMPT = PromptTemplate.from_template(
        """我是负责解决用户问题的 {role}，而你是我的助手 Assistant，我需要你根据我的指引来一步步回答用户 {user} 的问题，让用户更满意。
    """.strip()
    )

    ORIGIN_USER_INPUT_PROMPT = PromptTemplate.from_template("用户 {user} 的原始问题是：{question}")

    QUESTION_PROMPT = PromptTemplate.from_template(
        "综上所述，请简洁明了地回答用户的问题：{question}"
    )
    QUESTION_WITHOUT_PROMPT = PromptTemplate.from_template(
        "请简洁明了地回答用户的问题：{question}"
    )

    TOT_QUESTION_PROMPT = PromptTemplate.from_template(
        """对于用户的问题：{origin_question}
    我们已经尝试了以下步骤：
    {memory}
    如何进一步拆分解答步骤 {title}:{description}
    """.strip()
    )

    COT_QUESTION_DESCOMPOSITION_PROMPT = PromptTemplate.from_template(
        """对于用户的问题：{question}
    请按照我给步骤 {title}:{description}
    一步步详细地完善细节，如果可以的话希望尽可能细粒度到具体的人和物。比如说不要说天气不错，而是具体描述：天气晴、33度。
    """.strip()
    )

    # memory index 相关配置
    MEMORY_PROMPT = PromptTemplate.from_template(
        """
    在 {time},用户问了一个问题：
    {question}
    {events}
    完成上述步骤后，回答如下:
    {answer}
    {feedback}
    """
    )

    MEMORY_INDEX_URI = "http://localhost:19531"
    MEMORY_INDEX_TIMEOUT = 1
    MEMORY_COLLECTION_NAME = "memory_index"
    MEMORY_INDEX_TYPE = "IVF_FLAT"
    MEMORY_INDEX_METRIC_TYPE = "IP"
    MEMORY_INDEX_PARAMS = {"nlist": 128}
    LOCAL_TEST_MILVUS_PATH = "milvus_data"

    INDEX_VECTORIZE_MODEL = "all-MiniLM-L6-v2"
    INDEX_VECTORIZE_MODEL_DIM = 384

    # memory aid 相关配置
    MEMORY_AID_SIZE = 3
    MEMORY_AID_PROMPT = PromptTemplate.from_template(
        """
    {current}
    过去的类似的解答经验如下:
    {memory}
    现在我还有 {tools_size} 个步骤可以选择:
    {tools}
    不需要你直接回答这个问题，只需要回答你认为现在应该操作哪一个或者多个步骤，步骤越少越好，能让我的回答用户更满意，更接近问题的答案.
    """.strip()
    )

    # TODO avaiable events 相关配置
    REMEMBER_EVENTS_MEMORY_SIZE = 3
    AVAILABLE_EVENTS_PROMPT = PromptTemplate.from_template("{num}. {event}")

    # planning 相关 PRMOPT
    PLAN_STEP_SYSTEM_CONTEXT_PROMPT = PromptTemplate.from_template(
        """
    我是负责解决用户问题的 {role}，而你是我的助手 Assistant，我需要你协助我一起分析用户 {user} 的问题，对问题进行拆解。不需要你直接回答问题，需要你一步步拆解问题，将问题拆解为若干步骤，步骤越少越好，来帮助解决用户的问题，让用户更满意。
    """.strip()
    )
    PLAN_STEP_REFINE_ANSWER_PROMPT = PromptTemplate.from_template(
        """
    用户最初的问题：{question}
    经过之前的步骤，我总结的到了如下的答案：
    {current_answer}
    但是用户对我的回答不够满意，我们要再进一步分析用户的问题，对问题进行拆解。仍然不需要你直接回答问题，需要你一步步优化这个答案，将过程拆解为若干步骤，步骤越少越好，让用户更满意。
    """.strip()
    )
    # TODO example
    COT_ADJUST_PLANNING_QUESTION_PROMPT = PromptTemplate.from_template(
        """
    综上所述，我们已经尝试了以下步骤：
    {memory}
    你认为接下来我们选择哪一个步骤来优先尝试？请按照「步骤名称:步骤的详细做法」的格式来回答问题，1. 煎蛋皮：用平底锅煎中小火煎蛋皮。并且一定要在回复的最开头直接回答。
    """.strip()
    )
    COT_QUESTION_DESCOMPOSITION_PROMPT = PromptTemplate.from_template(
        """
    我们已经尝试了以下步骤：
    {memory}
    综上所述，对于当前的问题：
    {question}
    我们应该分成哪几个步骤来解决呢？最多我们可以分成{max_step}个步骤来尝试？请按照「序号.步骤名称：步骤的详细做法」的格式来描述每一个步骤，并且用换行符来分隔各个步骤。例如 1. 煎蛋皮：用平底锅煎中小火煎蛋皮。
    """.strip()
    )
    PLAN_STEP_REGEX = re.compile("(\d+)\.([^:]+)[:：](.+)\n")

    # memory aid 相关 PROMPT
    MEMORY_PREFIX_CONTEXT = """
    我记忆中之前处理过类似的问题：\n
    """.strip()
    MEMORY_CONCLUTION_QUESTION = "你认为其中有为你提供帮助的吗？"

    # web search 相关 PROMPT
    WEB_SEARCH_ENGINE_SYETEM_CONTEXT = PromptTemplate.from_template(
        "我是负责解决用户问题的 {role}，而你是我的助手 Google，我需要你帮我从互联网上寻找资料并总结，来帮我解决用户 {user} 的问题。"
    )
    SEARCH_WEB_PROMPT = PromptTemplate.from_template(
        "请从互联网上帮我查询「{query}」有关的{num}条结果，越新越重要越好"
    )
    WEB_SEARCH_PREFIX_CONTEXT = """我从互联网上收集了相关的资料。"""
    WEB_SEARCH_QUESTION = "你认为其中有为你提供帮助的吗？"

    # TOOL USE 相关 PROMPT
    TOOL_USE_PREFIX_CONTEXT = "除此之外，我们还有一些可选的步骤："
    TOOL_PROMPT = PromptTemplate.from_template("{num}. {title}:{description}")
    TOOL_USE_QUESTION = "你认为其中有哪些可以用的步骤？请回答的时候带上步骤的序号。"

    # reflection 相关 PROMPT
    REFLECTION_SYSTEM_CONTEXT = PromptTemplate.from_template(
        "我是负责解决用户问题的 {role}，而你是我的助手 Assistant，我需要你协助我一起优化之前的回答，让用户 {user} 对这个回答更满意。"
    )
    REFLECTION_QUESTION_PROMPT = PromptTemplate.from_template(
        """
    用户的问题：{question}
    我们之前采用了以下步骤：
    {actions}
    来解决这个问题，准备如此回复给用户：
    {current_answer}
    你觉得这个答案是否能让用户满意？请回答是或者否
    """.strip()
    )
    REFLECTION_DETECT_REGEX = "^是.*"

    # conclution 相关 PROMPT
    CONCLUDE_REFINE_QUESTION = """请帮我总结一下之前讨论的步骤以及上文所提及的关键信息，例如现在已经执行的步骤、来自外部（搜索、记忆）的关键参考资料、之前回答的不足点（如果有的话）等等。""".strip()

