from http import HTTPStatus

import pytest


LOGIN_ROUTE = '/auth/login/'


@pytest.mark.parametrize(
    'credentials,expected_status',
    [
        ({}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'login': 'login1'}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'password': 'pass1'}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'login': 'login1', 'password': 'pass1'}, HTTPStatus.OK),
        ({'login': 'incorrect', 'password': 'pass1'}, HTTPStatus.UNAUTHORIZED),
        ({'login': 'login1', 'password': 'incorrect'}, HTTPStatus.UNAUTHORIZED)
    ]
)
@pytest.mark.asyncio
async def test_login(post, credentials, expected_status):
    # Act
    status, body = await post(LOGIN_ROUTE, credentials)

    # Assert
    assert expected_status == status
    if status == HTTPStatus.OK:
        assert 'access_token' in body
        assert 'refresh_token' in body
