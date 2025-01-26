from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .elastic import ElasticService, get_elastic_service
from .redis import RedisService, get_redis_service
from .mixins import ServiceMixin
from models.film import FilmInfo, FilmItem
from models.common import ListRequest, SearchRequest


class FilmService(ServiceMixin):
    def __init__(self, redis_service: RedisService, elastic_service: ElasticService):
        self.redis_service = redis_service
        self.elastic_service = elastic_service
        self.valid_sort_options = {'imdb_rating': 'imdb_rating', 'title': 'title.raw'}

    async def get_film_by_id(self, film_id: str) -> FilmInfo | None:
        film = await self.redis_service.get_from_cache(self.get_film_by_id.__name__, film_id)
        if not film:
            film = await self.elastic_service.get_doc_by_id('movies', film_id)
            if not film:
                return None
            film = FilmInfo(**film)
            await self.redis_service.set_cache(self.get_film_by_id.__name__, film_id, value=film)
        return film

    async def get_film_list(self, request: ListRequest) -> list[FilmItem]:
        films = await self.redis_service.get_from_cache(self.get_film_list.__name__, request)
        if not films:
            films = await self.elastic_service.get_exact_docs('movies', request, ['genres'])
            if not films:
                return []
            films = [FilmItem(**film) for film in films]
            await self.redis_service.set_cache(self.get_film_list.__name__, request, value=films)
        return films

    async def search_films(self, request: SearchRequest) -> list[FilmItem]:
        films = await self.redis_service.get_from_cache(self.search_films.__name__, request)
        if not films:
            films = await self.elastic_service.search_docs('movies', request, ['title', 'description'])
            if not films:
                return []
            films = [FilmItem(**film) for film in films]
            await self.redis_service.set_cache(self.search_films.__name__, request, value=films)
        return films


@lru_cache()
def get_film_service(
        redis_service: Annotated[RedisService, Depends(get_redis_service)],
        elastic_service: Annotated[ElasticService, Depends(get_elastic_service)]
) -> FilmService:
    return FilmService(redis_service, elastic_service)
