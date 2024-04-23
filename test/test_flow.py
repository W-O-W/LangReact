import asyncio
import pytest

from applications.qwen_chat_application import QwenChatApplicationPlugin
from langreact.core.common.chunk import Chunk
from langreact.core.flow import Flow
from langreact.core.params import InvokeParams


def test_flow_basic(setup):
    flow = Flow([QwenChatApplicationPlugin()], "demo/conf/default.py")
    params = InvokeParams(application=QwenChatApplicationPlugin().sign())
    res = flow.invoke(
        "zhangli", Chunk(command="QUESTION", data="请问 123+321 等于多少？"), params
    )
    # kimi = get_new_kimi_chatbot()
    result = asyncio.run(res)
    print(result)


def test_flow_with_cot(setup):
    flow = Flow([QwenChatApplicationPlugin()], "demo/conf/default.py")
    params = InvokeParams(application=QwenChatApplicationPlugin().sign(),cot=True)
    res = flow.invoke(
        "zhangli", Chunk(command="QUESTION", data="请给我一份详细的北京旅游攻略"), params
    )
    result = asyncio.run(res)
    print(result)

def test_flow_with_cot_and_reflection(setup):
    flow = Flow([QwenChatApplicationPlugin()], "demo/conf/default.py")
    params = InvokeParams(application=QwenChatApplicationPlugin().sign(),cot=True,reflection=True)
    res = flow.invoke(
        "zhangli", Chunk(command="QUESTION", data="请给我一份详细的北京旅游攻略"), params
    )
    result = asyncio.run(res)
    print(result)
