from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .elastic import ElasticService, get_elastic_service
from .redis import RedisService, get_redis_service
from models.genre import Genre
from models.common import ListRequest
from .mixins import ServiceMixin


class GenreService(ServiceMixin):
    def __init__(self, elastic_service: ElasticService, redis_service: RedisService):
        self.elastic_service = elastic_service
        self.redis_service = redis_service
        self.valid_sort_options = {}

    async def get_genre_by_id(self, genre_id: str) -> Genre | None:
        genre = await self.redis_service.get_from_cache(self.get_genre_by_id.__name__, genre_id)
        if not genre:
            genre = await self.elastic_service.get_doc_by_id('genre', genre_id)
            if not genre:
                return None
            genre = Genre(**genre)
            await self.redis_service.set_cache(self.get_genre_by_id.__name__, genre_id, value=genre)
        return genre

    async def get_genres(self, request: ListRequest) -> list[Genre]:
        genres = await self.redis_service.get_from_cache(self.get_genres.__name__, request)
        if not genres:
            genres = await self.elastic_service.get_exact_docs('genre', request, ['name'])
            if not genres:
                return []
            genres = [Genre(**genre) for genre in genres]
            await self.redis_service.set_cache(self.get_genres.__name__, request, value=genres)
        return genres


@lru_cache()
def get_genre_service(
        elastic_service: Annotated[ElasticService, Depends(get_elastic_service)],
        redis_service: Annotated[RedisService, Depends(get_redis_service)]
) -> GenreService:
    return GenreService(elastic_service, redis_service)
