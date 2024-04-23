import abc
from http import HTTPStatus
import logging
import os
import random
from typing import List, Mapping

from openai import OpenAI
from dashscope import Generation

from langreact.core.configure.default import Configure


class Application(abc.ABC):
    def __init__(self, configure: Configure) -> None:
        self.configure = configure

    @abc.abstractmethod
    def new_session(self, context, system_context_text=""):
        """create new session"""
        # session.add_message(context.input_chunk,role="")


class Session:
    def __init__(self, application: Application):
        self.messages: List[Mapping[str, str]] = []
        self.application = application

    def add_message(self, text, role=""):
        if role == "":
            role = self.application.configure.DEFAULT_ROLE
        self.messages.append({"role": role, "content": text})

    def get_message_num(self, role):
        return len([message for message in self.messages if message["role"] == role])

    @abc.abstractmethod
    def invoke(self, text, role="", retry_num=-1, **kwargs) -> bool:
        """请求 LLM"""


class QwenSession(Session):
    def __init__(self, version, application):
        self.version = version
        super().__init__(application)

    def invoke(self, text, role="", retry_num=-1, **kwargs):
        retry_num = self.application.configure.DEFAULT_LLM_RETRY_NUM
        if role == "":
            role = self.application.configure.DEFAULT_ROLE
        self.messages.append({"role": role, "content": text})
        for i in range(retry_num):
            response = Generation.call(
                "qwen-{}".format(self.version),
                messages=self.messages,
                # 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
                seed=random.randint(1, 10000),
                # 将输出设置为"message"格式
                result_format="message",
                **kwargs
            )
            if response.status_code == HTTPStatus.OK:
                self.messages.append(
                    {
                        "role": response.output.choices[0]["message"]["role"],
                        "content": response.output.choices[0]["message"]["content"],
                    }
                )
                logging.info(response)
                return True
            else:
                logging.warning(
                    "[retry %d]:Request id: %s, Status code: %s, error code: %s, error message: %s"
                    % (
                        i + 1,
                        response.request_id,
                        response.status_code,
                        response.code,
                        response.message,
                    )
                )
        self.messages = self.messages[:-1]
        logging.error("请求 LLM 失败，请检查日志确认是否异常")
        return False


class OpenAISession(Session):
    def invoke(self, text, role="", retry_num=-1, **kwargs):
        retry_num = self.application.configure.DEFAULT_LLM_RETRY_NUM
        if role == "":
            role = self.application.configure.DEFAULT_ROLE
        self.messages.append({"role": role, "content": text})
        client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_BASE_URL"],
            max_retries=retry_num,
        )
        completion = client.chat.completions.create(
            model="moonshot-{}".format(self.model_version),
            messages=self.messages,
            **kwargs
        )
        result = completion.choices[0].message
        self.messages.append({"role": result.role, "content": result.content})
        logging.info(completion)
        return True


class QwenLMApplication(Application):
    def __init__(self, version, configure) -> None:
        self.version = version
        super().__init__(configure=configure)

    def new_session(self, context, system_context_text="") -> Session:
        assert "DASHSCOPE_API_KEY" in os.environ, "please set DASHSCOPE_API_KEY in env"
        session = QwenSession(self.version, self)
        if system_context_text != "":
            session.add_message(system_context_text, role="system")
        return session
