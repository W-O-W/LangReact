


from demo.conf.qwen_chat_configure import Configure
from langreact.core.configure.configure import get_global_configure


def test_import():
    assert get_global_configure().__repr__() == Configure().__repr__()