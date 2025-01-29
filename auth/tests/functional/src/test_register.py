from http import HTTPStatus

import pytest


REGISTER_ROUTE = '/auth/register/'


@pytest.mark.parametrize(
    'user_data,expected_status',
    [
        (
            {
                'first_name': 'test',
                'last_name': 'test',
                'login': 'login',
                'password': 'valid_pass1'
            },
            HTTPStatus.OK
        ),
        (
            {
                'first_name': 'test',
                'last_name': 'test',
                'login': 'login5',
                'password': 'weak_pass'
            },
            HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
            {
                'first_name': 'test',
                'last_name': 'test',
                'login': 'login1',
                'password': 'valid_pass1'
            },
            HTTPStatus.CONFLICT
        ),
        ({}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ]
)
@pytest.mark.asyncio
async def test_registration(post, get_current_users, user_data, expected_status):
    # Arrange
    expected_user_num = len(await get_current_users()) + 1

    # Act
    status, user_data = await post(REGISTER_ROUTE, user_data)

    # Assert
    assert expected_status == status
    if status == HTTPStatus.OK:
        assert 'id' in user_data
        assert 'login' in user_data
        assert 'first_name' in user_data
        assert 'last_name' in user_data
        assert expected_user_num == len(await get_current_users())
    if status >= HTTPStatus.BAD_REQUEST:
        assert expected_user_num - 1 == len(await get_current_users())
