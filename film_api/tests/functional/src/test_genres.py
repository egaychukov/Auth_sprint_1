import asyncio
from http import HTTPStatus

import pytest

GENRES_ROUTE = '/api/v1/genres/'


@pytest.mark.parametrize(
    'list_request,expected_status,expected_count',
    [
        ({}, HTTPStatus.OK, 13),
        ({'page_size': 1, 'page_number': 0}, HTTPStatus.OK, 1),
        ({'page_size': 0, 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY, None),
        ({'page_size': -1, 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY, None),
        ({'page_size': 1, 'page_number': -1}, HTTPStatus.UNPROCESSABLE_ENTITY, None),
        ({'page_size': 'text', 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY, None),
        ({'page_size': 1, 'page_number': 'text'}, HTTPStatus.UNPROCESSABLE_ENTITY, None),
    ]
)
@pytest.mark.asyncio
async def test_get_all_genres(get_json, list_request, expected_status, expected_count):
    status, body = await get_json(GENRES_ROUTE, list_request)
    assert status == expected_status
    if status == HTTPStatus.OK and expected_count is not None:
        assert len(body) == expected_count


@pytest.mark.parametrize(
    "genre_id, result_genre",
    [
        (
                "3d8d9bf5-0d90-4353-88ba-4ccc5d2c0701",
                {
                    "id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c0701",
                    "name": "Action"
                }
        ),
        (
                "120a21cf-9097-479e-904a-13dd7198c102",
                {
                    "id": "120a21cf-9097-479e-904a-13dd7198c102",
                    "name": "Adventure"
                }
        ),
        (
                "b92ef010-5e4c-4fd0-99d6-41b645627203",
                {
                    "id": "b92ef010-5e4c-4fd0-99d6-41b645627203",
                    "name": "Fantasy"
                }
        ),
    ]
)
@pytest.mark.asyncio
async def test_genre(get_json, genre_id, result_genre):
    status, body = await get_json(f'{GENRES_ROUTE}{genre_id}/', {})
    assert status == HTTPStatus.OK
    assert body == result_genre


@pytest.mark.parametrize(
    'list_request,expected_key_number',
    [
        ({}, 1),
        ({'page_number': 0, 'page_size': 1}, 1),
        ({'page_number': -1}, 0),
        ({'page_size': -1}, 0),
    ]
)
@pytest.mark.asyncio
async def test_redis_caching(get_json, redis_client, list_request, expected_key_number):
    QUERY_NUMBER = 5
    redis_client.flushdb()
    assert redis_client.dbsize() == 0
    tasks = []
    for _ in range(QUERY_NUMBER):
        tasks.append(get_json(GENRES_ROUTE, list_request))
    await asyncio.gather(*tasks)
    assert redis_client.dbsize() == expected_key_number
