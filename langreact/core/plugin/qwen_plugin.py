
from langreact.core.application import Application, QwenLMApplication
from langreact.core.plugin.plugins import ApplicationPlugin


class QwenTurboPlugin(ApplicationPlugin):
    def __init__(self):
        super().__init__("qwen", "0.1")

    def create_new_application(
        self, local_context, configure, reflection=False
    ) -> Application:
        return QwenLMApplication("turbo", configure)
