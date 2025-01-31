from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .elastic import ElasticService, get_elastic_service
from .redis import RedisService, get_redis_service
from models.person import PersonFilm, Person
from models.common import SearchRequest
from models.film import FilmInfo


class PersonService:
    def __init__(self, elastic_service: ElasticService, redis_service: RedisService):
        self.elastic_service = elastic_service
        self.redis_service = redis_service

    async def get_person_by_id(self, person_id: str) -> Person | None:
        person = await self.redis_service.get_from_cache(self.get_person_by_id.__name__, person_id)
        if not person:
            person = await self.elastic_service.get_doc_by_id('person', person_id)
            if not person:
                return None
            person = Person(**person)
            await self.redis_service.set_cache(self.get_person_by_id.__name__, person_id, value=person)
        return person

    async def get_person_films(self, person_id: str) -> list[FilmInfo]:
        films = await self.redis_service.get_from_cache(self.get_person_films.__name__, person_id)
        if not films:
            films = await self.elastic_service.get_exact_docs_by_nested(
                'movies',
                person_id,
                ['actors.id', 'directors.id', 'writers.id']
            )
            if not films:
                return []
            films = [FilmInfo(**film) for film in films]
            await self.redis_service.set_cache(self.get_person_films.__name__, person_id, value=films)
        return films

    async def get_person_film_roles(self, person_id) -> list[PersonFilm]:
        film_roles = await self.redis_service.get_from_cache(self.get_person_film_roles.__name__, person_id)
        if not film_roles:
            films = await self.get_person_films(person_id)
            if not films:
                return []
            film_roles = []
            for film in films:
                person_film = PersonFilm(id=film.id, roles=[])
                if person_id in [actor.id for actor in film.actors]:
                    person_film.roles.append('actor')
                if person_id in [writer.id for writer in film.writers]:
                    person_film.roles.append('writer')
                if person_id in [director.id for director in film.directors]:
                    person_film.roles.append('director')
                film_roles.append(person_film)
            await self.redis_service.set_cache(self.get_person_film_roles.__name__, person_id, value=film_roles)
        return film_roles

    async def search_persons(self, request: SearchRequest) -> list[Person]:
        people = await self.redis_service.get_from_cache(self.search_persons.__name__, request)
        if not people:
            people = await self.elastic_service.search_docs('person', request, ['full_name'])
            if not people:
                return []
            people = [Person(**person) for person in people]
            await self.redis_service.set_cache(self.search_persons.__name__, request, value=people)
        return people


@lru_cache()
def get_person_service(
        elastic_service: Annotated[ElasticService, Depends(get_elastic_service)],
        redis_service: Annotated[RedisService, Depends(get_redis_service)]
) -> PersonService:
    return PersonService(elastic_service, redis_service)
