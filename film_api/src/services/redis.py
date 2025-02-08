import pickle
from typing import Annotated

from redis import Redis
from fastapi import Depends

from core.config import settings
from db.redis import get_redis


class RedisService:
    def __init__(self, redis: Redis, cache_invalidation: int):
        self.redis = redis
        self.cache_invalidation = cache_invalidation

    async def get_from_cache(self, *args, **kwargs):
        key = self._get_cache_key(args, kwargs)
        cached_result = await self.redis.get(key)
        return pickle.loads(cached_result) if cached_result else None

    async def set_cache(self, *args, value, **kwargs):
        key = self._get_cache_key(args, kwargs)
        await self.redis.set(key, pickle.dumps(value), self.cache_invalidation)

    def _get_cache_key(self, *args, **kwargs):
        sorted_kwargs = sorted(kwargs.items())
        return pickle.dumps(args) + pickle.dumps(sorted_kwargs)


def get_redis_service(
        redis: Annotated[Redis, Depends(get_redis)]
) -> RedisService:
    return RedisService(redis, settings.default_cache_expiry_in_seconds)
