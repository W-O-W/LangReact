from datetime import datetime
import time
from typing import List
from pymilvus import MilvusClient, DataType, MilvusException
from sentence_transformers import SentenceTransformer

from langreact.core.memory.memory_chunk import GlobalMemoryChunk
import logging


class EncodeModel:
    def __init__(
        self,
        dim,
        model,
    ):
        self.dim = dim
        self.model = model

    def encode(self, *texts: List[str]):
        return self.model.encode(texts)


class MemoryIndex:
    def __init__(self,config, encoder_model: EncodeModel = None, **kwargs) -> None:
        self.client = MilvusClient(uri=config.MEMORY_INDEX_URI, **kwargs)
        self.encode_model = encoder_model
        self.config = config
        if self.encode_model is None:
            self.encode_model = EncodeModel(
                config.INDEX_VECTORIZE_MODEL_DIM,
                SentenceTransformer(config.INDEX_VECTORIZE_MODEL),
            )
        try:
            self.client.load_collection(config.MEMORY_COLLECTION_NAME)
            # TODO LOG
        except MilvusException as e:
            if e.code == 100:
                self.init_index_once()
                time.sleep(8)
                # TODO LOG
            else:
                raise e

    def init_index_once(self):
        schema = self.create_schema()
        config = self.config
        index_params = self.client.prepare_index_params()
        # index_params.add_index("id", index_type="STL_SORT")
        # index_params.add_index("day")
        index_params.add_index(
            "vector",
            index_type=config.MEMORY_INDEX_TYPE,
            metric_type=config.MEMORY_INDEX_METRIC_TYPE,
            params=config.MEMORY_INDEX_PARAMS,
        )
        self.client.create_collection(
            collection_name=config.MEMORY_COLLECTION_NAME,
            schema=schema,
            index_params=index_params,
        )

    def alive(self):
        # TODO check log
        load_state = self.client.get_load_state(
            self.config.MEMORY_COLLECTION_NAME
        )
        return load_state["state"].value == 3

    def create_schema(self):
        schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=False)
        schema.add_field("id", datatype=DataType.INT64, auto_id=True, is_primary=True)
        schema.add_field(
            "day",
            DataType.INT64,
            is_partition_key=True,
        )
        schema.add_field("content", DataType.JSON)
        schema.add_field(
            "vector", datatype=DataType.FLOAT_VECTOR, dim=self.encode_model.dim
        )
        schema.add_field("user", datatype=DataType.VARCHAR, max_length=200)
        return schema

    def insert(self, *memory_chunks: GlobalMemoryChunk):
        vectors = self.encode_model.encode(
            *[memory_chunk.to_natural_language(self.config) for memory_chunk in memory_chunks]
        )
        data = [
            dict(
                content=memory_chunk.to_json(),
                day=int(datetime.strftime(memory_chunk.happen_time, "%Y%m%d")),
                vector=vector,
                user=memory_chunk.user,
            )
            for memory_chunk, vector in zip(memory_chunks, vectors)
        ]
        # TODO LOG logging.info(">>>>>>>>>>>>>>{}".format(data[0]["vector"]))

        # TODO handle stat
        return self.client.insert(self.config.MEMORY_COLLECTION_NAME, data)

    # TODO 用户分组
    def search_from_scentences(
        self,
        *scentences,
        start_day=None,
        end_day=None,
        limit=5,
        limit_distance=None,
        limit_user=None
    ):
        vectors = self.encode_model.encode(*scentences)
        return self.search(
            *vectors,
            start_day=start_day,
            end_day=end_day,
            limit=limit,
            limit_distance=limit_distance,
            limit_user=limit_user
        )

    def search(
        self,
        *vectors,
        start_day=None,
        end_day=None,
        limit=5,
        limit_distance=None,
        limit_user=None
    ) -> List[List[GlobalMemoryChunk]]:
        # TODO LOG logging.info(vectors)
        filter_list = []
        if start_day is not None or end_day is not None:
            if start_day == end_day:
                filter = "day = {}".format(start_day)
            elif start_day is None:
                filter = "day <= {}".format(end_day)
            elif end_day is None:
                filter = "day >= {}".format(start_day)
            else:
                filter = "day >= {} and day <= {}".format(start_day, end_day)
            filter_list.append(filter)

        if limit_user is not None:
            filter_list.append("user = '{}'".format(limit_distance))

        memory_data = self.client.search(
            collection_name=self.config.MEMORY_COLLECTION_NAME,
            data=list(vectors),
            limit=limit,
            filter=" AND ".join(filter_list),
            output_fields=["content"],
        )
        total_chunks = []
        for _, datas in zip(vectors, memory_data):
            chunks = []
            for data in datas:
                if limit_distance is None or data["distance"] >= limit_distance:
                    chunk = GlobalMemoryChunk.from_json("", data["entity"]["content"])
                    chunk.data = {"distance": data["distance"], "id": data["id"]}
                    chunks.append(chunk)
                elif limit_distance is not None and data["distance"] < limit_distance:
                    logging.debug(
                        "skip {} due to distance < {}".format(data, limit_distance)
                    )

            chunks.sort(key=lambda x: x.happen_time.timestamp())
            total_chunks.append(chunks)
        return total_chunks
