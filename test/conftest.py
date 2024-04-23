
import logging
import pytest

from demo.simple_milvus_server import close_default_server, start_default_server





@pytest.fixture(name = "setup",scope="session")
def setup(request):
    logging.info(">>>>>>>>>>>>>INIT")
    close_default_server()
    start_default_server(True)

    def teardown_module():
        logging.info(">>>>>>>>>>>>>STOP")
        close_default_server()
        
    request.addfinalizer(teardown_module)
