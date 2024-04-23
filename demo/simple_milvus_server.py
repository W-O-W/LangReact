
from milvus import default_server

from langreact.core.configure.configure import get_global_configure


default_server.set_base_dir(get_global_configure().LOCAL_TEST_MILVUS_PATH)
default_server.config.set('proxy_port', int(get_global_configure().MEMORY_INDEX_URI.split(":")[-1]))

def start_default_server(cleanup=False):
    if cleanup:
        default_server.cleanup()
    default_server.start()

def close_default_server():
    default_server.stop()
