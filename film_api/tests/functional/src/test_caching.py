import pytest
import asyncio

FILMS_ROUTE = '/api/v1/films/'
FILM_SEARCH_ROUTE = f'{FILMS_ROUTE}search'
PERSON_ROUTE = '/api/v1/persons/'
PERSON_SEARCH_ROUTE = f'{PERSON_ROUTE}search'


@pytest.mark.parametrize(
    'query,expected_key_number',
    [
        ({}, 1),
        ({'page_number': 0, 'page_size': 1, 'sort': '+title', 'genre': 'Action'}, 1),
        ({'sort': '+title', 'genre': 'Action'}, 1),
        ({'page_number': 0, 'page_size': 1, 'genre': 'Action'}, 1),
        ({'page_number': 0, 'page_size': 1, 'sort': '+title'}, 1),
        ({'page_number': -1}, 0),
        ({'page_size': -1}, 0),
        ({'sort': '-nonexistent'}, 0),
        ({'sort': 'no_sign'}, 0),
        ({'genre': 'nonexistent'}, 0)
    ]
)
@pytest.mark.asyncio
async def test_film_list_cache(get_json, redis_client, query, expected_key_number):
    await _test_redis_caching(
        get_json,
        redis_client,
        FILMS_ROUTE,
        query,
        expected_key_number)


@pytest.mark.parametrize(
    'film_id,expected_key_number',
    [
        ('2a090dde-f688-46fe-a9f4-b781a985275e', 1),
        ('b9151ead-cf2f-4e14-aeb9-c4617f68848f', 1),
        ('nonexistent', 0),
    ]
)
@pytest.mark.asyncio
async def test_get_film_by_id_cache(get_json, redis_client, film_id, expected_key_number):
    await _test_redis_caching(
        get_json,
        redis_client,
        f'{FILMS_ROUTE}{film_id}',
        {},
        expected_key_number)


@pytest.mark.parametrize(
    'search_query,expected_key_number',
    [
        ({'query': 'Star', 'page_number': 0, 'page_size': 1}, 1),
        ({'query': 'nonexistent', 'page_number': 0, 'page_size': 1}, 0),
        ({'query': '', 'page_number': 0, 'page_size': 1}, 0),
        ({'query': 'Star', 'page_number': 0, 'page_size': -1}, 0),
        ({'query': 'Star', 'page_number': 0, 'page_size': 0}, 0),
        ({'query': 'Star', 'page_number': -1, 'page_size': 1}, 0),
        ({'page_number': 0, 'page_size': 1}, 0),
        ({'query': 'Star', 'page_size': 1}, 0),
        ({'query': 'Star', 'page_number': 0}, 0),
    ]
)
@pytest.mark.asyncio
async def test_film_search_cache(get_json, redis_client, search_query, expected_key_number):
    await _test_redis_caching(
        get_json,
        redis_client,
        FILM_SEARCH_ROUTE,
        search_query,
        expected_key_number)


@pytest.mark.parametrize(
    'search_query,expected_key_number',
    [
        ({'query': 'James', 'page_number': 0, 'page_size': 1}, 3),
        ({'query': 'nonexistent', 'page_number': 0, 'page_size': 1}, 0),
        ({'query': '', 'page_number': 0, 'page_size': 1}, 0),
        ({'query': 'James', 'page_number': 0, 'page_size': -1}, 0),
        ({'query': 'James', 'page_number': 0, 'page_size': 0}, 0),
        ({'query': 'James', 'page_number': -1, 'page_size': 1}, 0),
        ({'page_number': 0, 'page_size': 1}, 0),
        ({'query': 'James', 'page_size': 1}, 0),
        ({'query': 'James', 'page_number': 'text-data', 'page_size': 1}, 0),
        ({'query': 'James', 'page_number': 0, 'page_size': 'text-data'}, 0),
        ({'query': 'James', 'page_number': 0}, 0),
    ]
)
@pytest.mark.asyncio
async def test_person_search_cache(get_json, redis_client, search_query, expected_key_number):
    await _test_redis_caching(
        get_json,
        redis_client,
        PERSON_SEARCH_ROUTE,
        search_query,
        expected_key_number)


@pytest.mark.parametrize(
    'person_id,expected_key_number',
    [
        ('a18cbb60-f0ec-4a87-ad37-3e48d8cf3735', 1),
        ('nonexistent', 0),
        ('', 0),
    ]
)
@pytest.mark.asyncio
async def test_person_films_cache(get_json, redis_client, person_id, expected_key_number):
    await _test_redis_caching(
        get_json,
        redis_client,
        f'{PERSON_ROUTE}{person_id}/film',
        {},
        expected_key_number)


async def _test_redis_caching(get_json, redis_client, route, query, expected_key_number):
    QUERY_NUMBER = 5
    redis_client.flushdb()
    assert redis_client.dbsize() == 0
    tasks = []
    for _ in range(QUERY_NUMBER):
        tasks.append(get_json(route, query))
    await asyncio.gather(*tasks)
    assert redis_client.dbsize() == expected_key_number
