import logging
import backoff
from elasticsearch import Elasticsearch
from settings import test_settings

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, Exception, max_time=300)
def connect(client: Elasticsearch) -> None:
    if not client.ping():
        raise ValueError("Failed to connect")

    logger.info("Elasticsearch connected")


if __name__ == "__main__":
    es_client = Elasticsearch(hosts=test_settings.get_es_url())
    connect(es_client)
