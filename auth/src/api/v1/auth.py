from typing import Annotated
from http import HTTPStatus

from jose.exceptions import JWTError, ExpiredSignatureError
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer

from models.user import UserResponse, UserCreateRequest
from services.user import UserService, get_user_service
from services.token import TokenService, get_token_service


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
    if not user or not (await user_service.check_password(user.id, password)):
        raise HTTPException(HTTPStatus.BAD_REQUEST, 'Invalid credentials')
    return {
        'access_token': token_service.create_access_token(user.id),
        'refresh_token': token_service.create_refresh_token(user.id),
    }


@router.post('/refresh/')
async def refresh(
        token: Annotated[str, Depends(oauth2_scheme)],
        token_service: Annotated[TokenService, Depends(get_token_service)]
) -> dict[str, str]:
    token_subject = _get_token_subject(token, token_service)
    if not token_service.exists(token_subject, token):
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Invalid refresh token')
    token_service.revoke_refresh_token(token_subject, token)
    return {
        'access_token': token_service.create_access_token(token_subject),
        'refresh_token': token_service.create_refresh_token(token_subject),
    }


def _get_token_subject(token: str, token_service: TokenService):
    try:
        return token_service.get_payload(token).get('sub')
    except (JWTError, ExpiredSignatureError):
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Invalid refresh token')
