import logging

import backoff
from redis import Redis

from settings import test_settings

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, Exception, max_time=300)
def connect(client: Redis) -> None:
    client.ping()
    logger.info("Redis connected")


if __name__ == "__main__":
    redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port, decode_responses=True)
    connect(redis)
