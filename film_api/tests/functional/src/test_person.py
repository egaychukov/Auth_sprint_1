from http import HTTPStatus

import pytest

PERSON_ROUTE = '/api/v1/persons'
PERSON_SEARCH_ROUTE = f'{PERSON_ROUTE}/search'


@pytest.mark.parametrize(
    'search_request,expected_status',
    [
        ({'query': 'Test', 'page_number': 0, 'page_size': 1}, HTTPStatus.OK),
        ({'query': 'Test', 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Test', 'page_size': 1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'page_size': 1, 'page_number': 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Test', 'page_number': -1, 'page_size': 1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Test', 'page_number': 0, 'page_size': 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Test', 'page_number': 0, 'page_size': -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Test', 'page_number': 'text-data', 'page_size': 1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'query': 'Test', 'page_number': 0, 'page_size': 'text-data'}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ]
)
@pytest.mark.asyncio
async def test_search_validation(get_json, search_request, expected_status):
    status, _ = await get_json(PERSON_SEARCH_ROUTE, search_request)
    assert status == expected_status


@pytest.mark.parametrize(
    'search_request,expected_len',
    [
        ({'query': 'James', 'page_number': 0, 'page_size': 1}, 1),
        ({'query': 'James', 'page_number': 1, 'page_size': 2}, 1),
        ({'query': 'James', 'page_number': 0, 'page_size': 3}, 3),
        ({'query': 'James', 'page_number': 0, 'page_size': 5}, 3),
    ]
)
@pytest.mark.asyncio
async def test_search_pagination(get_json, search_request, expected_len):
    status, body = await get_json(PERSON_SEARCH_ROUTE, search_request)
    assert status == HTTPStatus.OK
    assert len(body) == expected_len


@pytest.mark.parametrize(
    'query,expected_len',
    [
        ('James', 3),
        ('Ray', 1),
        ('nonexistent', 0),
        ('', 0),
    ]
)
@pytest.mark.asyncio
async def test_search(get_json, person_data, query, expected_len):
    status, body = await get_json(PERSON_SEARCH_ROUTE, {
        'query': query,
        'page_number': 0,
        'page_size': len(person_data)
    })
    assert status == HTTPStatus.OK
    assert len(body) == expected_len


@pytest.mark.parametrize(
    'person_id,expected_status',
    [
        ('4959e5b7-d157-4cdf-bc4f-5eb3cf8bd57f', HTTPStatus.OK),
        ('4f27971e-c80a-4894-be67-721fe7ff6a7f', HTTPStatus.OK),
        ('nonexistent', HTTPStatus.NOT_FOUND)
    ]
)
@pytest.mark.asyncio
async def test_search_by_id(get_json, person_data, person_id, expected_status):
    expected = [person for person in person_data if person['id'] == person_id]
    status, body = await get_json(PERSON_ROUTE + f'/{person_id}', {})
    assert status == expected_status
    if expected:
        assert body['full_name'] == expected[0]['full_name']


@pytest.mark.parametrize(
    'person_id,expected_film_number',
    [
        ('a18cbb60-f0ec-4a87-ad37-3e48d8cf3735', 2),
        ('ddc8d633-79d5-4313-ad44-45e2ece6602b', 1),
        ('4d6c07c3-6ca4-48b1-8c15-4b31d8fc7321', 0),
        ('nonexistent', 0),
    ]
)
@pytest.mark.asyncio
async def test_get_person_films(get_json, person_id, expected_film_number):
    status, body = await get_json(f'{PERSON_ROUTE}/{person_id}/film', {})
    assert status == HTTPStatus.OK
    assert len(body) == expected_film_number
