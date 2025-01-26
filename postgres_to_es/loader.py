import logging

import backoff
from elasticsearch import Elasticsearch, ApiError, TransportError, helpers


class ElasticSearchLoader:
    def __init__(self, es_client: Elasticsearch):
        self.es_client = es_client

    @backoff.on_exception(wait_gen=backoff.expo, exception=(ApiError, TransportError))
    def load_data(self, data: list[dict], index_name: str) -> None:
        def generate_docs() -> dict[str, str | dict]:
            for doc in data:
                yield {
                    "_index": index_name,
                    "_id": doc["id"],
                    "_source": doc,
                }

        helpers.bulk(self.es_client, generate_docs())
        logging.info(f"Loading to ElasticSearch (index: {index_name}) successfully.")
