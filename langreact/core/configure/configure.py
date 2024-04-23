from dataclasses import asdict, replace
import importlib
import importlib.util
from langreact.core.configure.default import Configure

configure_cache = {}


def get_global_configure(path=None, name="Configure") -> Configure:
    if path is None:
        return Configure()
    cache_key = path + ":" + name
    if cache_key in configure_cache:
        return configure_cache[cache_key]
    configure_spec = importlib.util.spec_from_file_location("conf", path)
    configure_module = importlib.util.module_from_spec(configure_spec)
    configure_spec.loader.exec_module(configure_module)
    conf = getattr(configure_module, name)()
    configure_cache[cache_key] = replace(Configure(), **asdict(conf))
    return configure_cache[cache_key]
