from http import HTTPStatus

import pytest

FILM_SEARCH_ROUTE = '/api/v1/films/search'


@pytest.mark.parametrize(
    'search_request,expected',
    [
        ({'query': 'Star'}, {'status': HTTPStatus.OK, 'len': 5}),
        ({'query': 'Voyage'}, {'status': HTTPStatus.OK, 'len': 1}),
        ({'query': 'ferocity'}, {'status': HTTPStatus.OK, 'len': 1}),
        ({'query': 'nonexistent rubbish'}, {'status': HTTPStatus.OK, 'len': 0}),
        ({'query': ''}, {'status': HTTPStatus.OK, 'len': 0}),
    ]
)
@pytest.mark.asyncio
async def test_search_by_query(get_json, film_data, search_request, expected):
    query = {
        'query': search_request['query'],
        'page_number': 0,
        'page_size': len(film_data)
    }
    status, body = await get_json(FILM_SEARCH_ROUTE, query)
    assert status == expected['status']
    assert len(body) == expected['len']


@pytest.mark.parametrize(
    'search_request,expected_status',
    [
        ({'query': 'Star', 'page_number': 0, 'page_size': 2}, HTTPStatus.OK),
        ({'query': 'Star', 'page_number': 1, 'page_size': 2}, HTTPStatus.OK),
        ({'query': 'Star', 'page_number': 1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Star', 'page_size': 2}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Star', 'page_number': 'text_data', 'page_size': 1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Star', 'page_number': 0, 'page_size': 'text_data'}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 1, 'page_number': 0, 'page_size': 1}, HTTPStatus.OK),
        ({'query': 'Star', 'page_number': -1, 'page_size': 2}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Star', 'page_number': 0, 'page_size': 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Star', 'page_number': 0, 'page_size': -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'page_number': 0, 'page_size': 1}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ]
)
@pytest.mark.asyncio
async def test_validation(get_json, search_request, expected_status):
    status, _ = await get_json(FILM_SEARCH_ROUTE, search_request)
    assert status == expected_status


@pytest.mark.parametrize(
    'search_request,expected_len',
    [
        ({'query': 'Star', 'page_size': 1, 'page_number': 0}, 1),
        ({'query': 'Star', 'page_size': 2, 'page_number': 0}, 2),
        ({'query': 'Star', 'page_size': 1, 'page_number': 1}, 1),
        ({'query': 'Star', 'page_size': 2, 'page_number': 1}, 2),
        ({'query': 'Star', 'page_size': 100, 'page_number': 0}, 5),
        ({'query': 'Star', 'page_size': 100, 'page_number': 1}, 0),
        ({'query': 'Star', 'page_size': 2, 'page_number': 2}, 1),
    ]
)
@pytest.mark.asyncio
async def test_pagination(get_json, search_request, expected_len):
    status, body = await get_json(FILM_SEARCH_ROUTE, search_request)
    assert status == HTTPStatus.OK
    assert len(body) == expected_len
