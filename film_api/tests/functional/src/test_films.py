from http import HTTPStatus

import pytest

FILMS_ROUTE = '/api/v1/films/'


@pytest.mark.parametrize(
    'list_request,expected_status',
    [
        ({}, HTTPStatus.OK),
        ({'page_size': 1, 'page_number': 0, 'genre': 'Action', 'sort': '-imdb_rating'}, HTTPStatus.OK),
        ({'page_size': 0, 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'page_size': -1, 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'page_size': 1, 'page_number': -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'page_size': 'text', 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'page_size': 1, 'page_number': 'text'}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'sort': '-nonexistent'}, HTTPStatus.BAD_REQUEST),
        ({'sort': 'no_sign'}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ]
)
@pytest.mark.asyncio
async def test_validation(get_json, list_request, expected_status):
    status, _ = await get_json(FILMS_ROUTE, list_request)
    assert status == expected_status


@pytest.mark.parametrize(
    'list_request,expected_len',
    [
        ({}, 5),
        ({'page_size': 1, 'page_number': 0}, 1),
        ({'page_size': 5, 'page_number': 0}, 5),
        ({'page_size': 2, 'page_number': 1}, 2),
        ({'page_size': 3, 'page_number': 1}, 2),
        ({'page_size': 5, 'page_number': 1}, 0),
    ]
)
@pytest.mark.asyncio
async def test_pagination(get_json, list_request, expected_len):
    status, body = await get_json(FILMS_ROUTE, list_request)
    assert status == HTTPStatus.OK
    assert len(body) == expected_len


@pytest.mark.parametrize(
    'sort',
    [
        '-imdb_rating',
        '+imdb_rating',
        '-title',
        '+title',
    ]
)
@pytest.mark.asyncio
async def test_sorting(get_json, film_data, sort):
    expected = list(map(
        lambda f: f['id'],
        sorted(
            film_data,
            reverse=(sort[0] == '-'),
            key=lambda f: f[sort[1:]]
        )
    ))
    status, body = await get_json(FILMS_ROUTE, {'sort': sort})
    assert status == HTTPStatus.OK
    assert [film['id'] for film in body] == expected


@pytest.mark.parametrize(
    'genre,expected_len',
    [
        ('Action', 2),
        ('Adventure', 2),
        ('Horror', 1),
        ('Nonexistent', 0),
        ('Actio', 0),
        ('', 5)
    ]
)
@pytest.mark.asyncio
async def test_genre_filter(get_json, genre, expected_len):
    status, body = await get_json(FILMS_ROUTE, {'genre': genre})
    assert status == HTTPStatus.OK
    assert len(body) == expected_len


@pytest.mark.parametrize(
    'film_id,expected_status',
    [
        ('2a090dde-f688-46fe-a9f4-b781a985275e', HTTPStatus.OK),
        ('b9151ead-cf2f-4e14-aeb9-c4617f68848f', HTTPStatus.OK),
        ('nonexistent', HTTPStatus.NOT_FOUND),
    ]
)
@pytest.mark.asyncio
async def test_search_by_id(get_json, film_data, film_id, expected_status):
    expected = [film for film in film_data if film['id'] == film_id]
    status, body = await get_json(FILMS_ROUTE + film_id, {})
    assert status == expected_status
    assert body == expected[0] if expected else {'detail': 'film not found'}
