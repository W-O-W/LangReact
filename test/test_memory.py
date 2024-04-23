
import time
from langreact.core.common.chunk import Chunk
from langreact.core.memory.memory_index import MemoryIndex
from langreact.core.configure.configure import get_global_configure
from langreact.core.memory.memory_chunk import GlobalMemoryChunk
import logging

def test_memory_index(setup):
    memory_chunk_index = MemoryIndex(get_global_configure())
    assert memory_chunk_index.alive()
    x = GlobalMemoryChunk(begining_chunk=Chunk("A",data="go home"), end_chunk=Chunk("B",data="go home"))
    y = GlobalMemoryChunk(begining_chunk=Chunk("A",data="go home"), end_chunk=Chunk("B",data="go hospital"))
    z = GlobalMemoryChunk(begining_chunk=Chunk("A",data="go hospital"), end_chunk=Chunk("B",data="go hospital"))
    logging.info(
        "{}|{}|{}".format(x.to_natural_language(),y.to_natural_language(),z.to_natural_language())
    )
    status = memory_chunk_index.insert(x,y,z)
    time.sleep(10)
    logging.info("status:{}".format(status))
    assert status['insert_count'] == 3
    # logging.info(memory_chunk_index.client.get_collection_stats(get_global_configure().MEMORY_COLLECTION_NAME))
    get_res = memory_chunk_index.client.get(get_global_configure().MEMORY_COLLECTION_NAME,ids = status['ids'][0])
    logging.info("get_res:{}={}".format(status['ids'][0],get_res))
    search_res_1 = memory_chunk_index.search(get_res[0]['vector'],limit = 2)
    search_res_2 = memory_chunk_index.search_from_scentences(x.to_natural_language(),limit = 2)
    logging.info("{} ===== {}".format(search_res_1,search_res_2))
    assert search_res_1[0][0].to_natural_language() == search_res_2[0][0].to_natural_language()
    assert search_res_1[0][1] == search_res_2[0][1]
    logging.info("{} ===== {}".format(search_res_1[0][0].to_natural_language(),search_res_1[0][1].to_natural_language()))

