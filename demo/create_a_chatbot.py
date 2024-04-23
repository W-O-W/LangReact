import asyncio
from dataclasses import dataclass
from applications.qwen_chat_application import QwenChatApplicationPlugin
from langreact.core.common.chunk import Chunk
from langreact.core.flow import Flow
from langreact.core.params import InvokeParams
from demo.simple_milvus_server import close_default_server, start_default_server


plugins = [
    QwenChatApplicationPlugin()
]

application = "qwen_chat-0.1"
configure_path = "demo/conf/qwen_chat_configure.py"

# add DASHSCOPE_API_KEY to env

flow = Flow(plugins,configure_path)

# chat with cot
@dataclass(kw_only=True)
class Params(InvokeParams):
    application:str = application
    cot:bool = True
    

if __name__ == "__main__":
    # start_default_server()
    try:
        user = "test"
        question = Chunk(data = "今天天气如何")
        params = Params()
        request = flow.invoke(
            user=user,
            origin_input_chunk=question,
            params=params
        )
        print(asyncio.run(request))
    finally:
        pass
        # close_default_server()



