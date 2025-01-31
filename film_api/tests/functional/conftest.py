import json
from typing import Any
from pathlib import Path

import pytest
import asyncio
import pytest_asyncio
from redis import Redis
from aiohttp import ClientSession
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from settings import test_settings

index_definition = {
    'movies': Path('/app') / 'testdata' / 'films_es_schema.json',
    'genre': Path('/app') / 'testdata' / 'genres_es_schema.json',
    'person': Path('/app') / 'testdata' / 'person_es_schema.json',
}


@pytest_asyncio.fixture(scope='session')
def create_index(es_client: AsyncElasticsearch):
    async def inner(index: str):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)
        with open(index_definition[index]) as schema_file:
            index_mapping = json.load(schema_file)
        await es_client.indices.create(index=index, **index_mapping)

    return inner


@pytest_asyncio.fixture(scope='session')
def write_to_es(es_client: AsyncElasticsearch, create_index):
    async def inner(index: str, actions: list[dict[str, Any]]):
        await create_index(index)
        await async_bulk(client=es_client, actions=actions)
        await es_client.indices.refresh(index=index)

    return inner


@pytest_asyncio.fixture(scope='session')
async def es_client():
    es_client = AsyncElasticsearch(
        test_settings.get_es_url(),
        verify_certs=False
    )
    yield es_client
    await es_client.close()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture
def get_json(aiohttp_session: ClientSession):
    async def inner(api_route: str, params: dict[str, str]):
        async with aiohttp_session.get(api_route, params=params) as response:
            return response.status, await response.json()

    return inner


@pytest_asyncio.fixture(scope='session')
async def aiohttp_session():
    async with ClientSession(test_settings.get_service_url()) as session:
        yield session


@pytest.fixture(scope='session')
def film_data():
    with open(Path('/app') / 'testdata' / 'films.json') as films:
        yield json.load(films)


@pytest.fixture(scope='session')
def genre_data():
    with open(Path('/app') / 'testdata' / 'genres.json') as genres:
        yield json.load(genres)


@pytest.fixture(scope='session')
def redis_client():
    redis_client = Redis(test_settings.redis_host, test_settings.redis_port)
    yield redis_client
    redis_client.close()


@pytest_asyncio.fixture(autouse=True, scope='session')
async def set_up_genre_index(genre_data, write_to_es):
    actions = [{
        '_index': test_settings.es_genres_index,
        '_id': genre['id'],
        '_source': genre
    } for genre in genre_data]
    await write_to_es(test_settings.es_genres_index, actions)


@pytest_asyncio.fixture(autouse=True, scope='session')
async def set_up_film_index(film_data, write_to_es):
    actions = [{
        '_index': test_settings.es_films_index,
        '_id': film['id'],
        '_source': film
    } for film in film_data]
    await write_to_es(test_settings.es_films_index, actions)


@pytest.fixture(scope='session')
def person_data():
    with open(Path('/app') / 'testdata' / 'people.json') as people:
        yield json.load(people)


@pytest_asyncio.fixture(autouse=True, scope='session')
async def set_up_person_index(person_data, write_to_es):
    actions = [{
        '_index': test_settings.es_person_index,
        '_id': person['id'],
        '_source': person
    } for person in person_data]
    await write_to_es(test_settings.es_person_index, actions)
