from typing import Annotated
from abc import ABC, abstractmethod

from redis import Redis
from fastapi import Depends

from db.redis import get_redis
from core.config import settings


class TokenStorageService(ABC):
    @abstractmethod
    def add_access_token(self, key, token) -> None:
        pass

    @abstractmethod
    def add_refresh_token(self, key, token) -> None:
        pass

    @abstractmethod
    def get_token(self, key) -> str:
        pass

    @abstractmethod
    def remove_token(self, key) -> None:
        pass


class RedisTokenStorageService(TokenStorageService):
    def __init__(self, redis: Redis):
        self.redis = redis

    def add_access_token(self, key, token):
        self.redis.set(key, token, ex=settings.access_token_expire_minutes * 60)

    def add_refresh_token(self, key, token):
        self.redis.set(key, token, ex=settings.refresh_token_expire_minutes * 60)

    def get_token(self, key) -> str:
        return self.redis.get(key)

    def remove_token(self, key):
        self.redis.delete(key)


def get_token_storage_service(
        redis: Annotated[Redis, Depends(get_redis)]
) -> TokenStorageService:
    return RedisTokenStorageService(redis)
