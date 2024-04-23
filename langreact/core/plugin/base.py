from dataclasses import dataclass, field


@dataclass(unsafe_hash=True)
class Plugin:

    name: str
    version: str = field(default="0.0.1")

    def classname() -> str:
        return __name__

    def init(self, global_context) -> bool:
        return True

    def sign(self) -> str:
        return self.name + "-" + self.version
