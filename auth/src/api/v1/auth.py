from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Body

from models.user import UserResponse, UserCreateRequest
from services.user import UserService, get_user_service
from services.token import TokenService, get_token_service


router = APIRouter()


@router.post('/register/', response_model=UserResponse)
async def register(
        request: UserCreateRequest,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    if await user_service.get_by_login(request.login):
        raise HTTPException(HTTPStatus.BAD_REQUEST, 'The login already exists')
    return await user_service.create_user(request)


@router.post('/login/')
async def login(
        login: Annotated[str, Body()],
        password: Annotated[str, Body()],
        user_service: Annotated[UserService, Depends(get_user_service)],
        token_service: Annotated[TokenService, Depends(get_token_service)]
) -> dict[str, str]:
    user = await user_service.get_by_login(login)
    if not user:
        raise HTTPException(HTTPStatus.BAD_REQUEST, 'Invalid credentials')
    if not (await user_service.check_password(user.id, password)):
        raise HTTPException(HTTPStatus.BAD_REQUEST, 'Invalid credentials')
    return {
        'access_token': token_service.create_access_token(user.id),
        'refresh_token': token_service.create_refresh_token(user.id),
    }
