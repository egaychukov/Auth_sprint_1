from http import HTTPStatus

import pytest


LOGOUT_ROUTE = '/auth/logout/'


@pytest.mark.asyncio
async def test_valid_logout(post):
    # Arrange
    status, tokens = await post(
        '/auth/login/',
        {'login': 'login1', 'password': 'pass1'}
    )
    assert status < HTTPStatus.BAD_REQUEST

    headers = {
        'Authorization': 'Bearer ' + tokens['access_token'],
        'refresh-token': tokens['refresh_token']
    }

    # Act
    status, _ = await post(
        LOGOUT_ROUTE,
        body=None,
        headers=headers
    )

    # Assert
    assert status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_invalid_access_token_logout(post):
    # Arrange
    status, tokens = await post(
        '/auth/login/',
        {'login': 'login1', 'password': 'pass1'}
    )
    assert status < HTTPStatus.BAD_REQUEST

    headers = {
        'Authorization': 'Bearer incorrect_token',
        'refresh-token': tokens['refresh_token']
    }

    # Act
    status, _ = await post(
        LOGOUT_ROUTE,
        body=None,
        headers=headers
    )

    # Assert
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_invalid_refresh_token_logout(post):
    # Arrange
    status, tokens = await post(
        '/auth/login/',
        {'login': 'login1', 'password': 'pass1'}
    )
    assert status < HTTPStatus.BAD_REQUEST

    headers = {
        'Authorization': 'Bearer ' + tokens['access_token'],
        'refresh-token': 'incorrect_token'
    }

    # Act
    status, _ = await post(
        LOGOUT_ROUTE,
        body=None,
        headers=headers
    )

    # Assert
    assert status == HTTPStatus.UNAUTHORIZED