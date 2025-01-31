from typing import Annotated
from http import HTTPStatus

from jose.exceptions import JWTError, ExpiredSignatureError
from fastapi import APIRouter, Depends, HTTPException, Body, Header, Response
from fastapi.security import OAuth2PasswordBearer

from models.user import UserResponse, UserCreateRequest
from services.user import UserService, get_user_service
from services.token import TokenService, get_token_service


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post('/register/', response_model=UserResponse)
async def register(
        request: UserCreateRequest,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    if await user_service.get_by_login(request.login):
        raise HTTPException(HTTPStatus.CONFLICT, 'The login already exists')
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
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Invalid credentials')
    return {
        'access_token': token_service.create_access_token(user.id),
        'refresh_token': token_service.create_refresh_token(user.id),
    }


@router.post('/refresh/')
def refresh(
        refresh_token: Annotated[str, Depends(oauth2_scheme)],
        token_service: Annotated[TokenService, Depends(get_token_service)]
) -> dict[str, str]:
    token_subject = _get_token_subject(refresh_token, token_service)
    if token_service.is_refresh_token_revoked(token_subject, refresh_token):
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Invalid refresh token')
    token_service.revoke_refresh_token(token_subject, refresh_token)
    return {
        'access_token': token_service.create_access_token(token_subject),
        'refresh_token': token_service.create_refresh_token(token_subject),
    }


@router.post('/logout/')
def logout(
        access_token: Annotated[str, Depends(oauth2_scheme)],
        refresh_token: Annotated[str, Header()],
        token_service: Annotated[TokenService, Depends(get_token_service)]
):
    invalid_token_error = HTTPException(HTTPStatus.UNAUTHORIZED)
    access_token_subject = _get_token_subject(access_token, token_service)
    if token_service.is_access_token_revoked(access_token_subject, access_token):
        raise invalid_token_error
    refresh_token_subject = _get_token_subject(refresh_token, token_service)
    if token_service.is_refresh_token_revoked(refresh_token_subject, refresh_token):
        raise invalid_token_error
    if access_token_subject != refresh_token_subject:
        raise invalid_token_error
    token_service.revoke_access_token(access_token_subject, access_token)
    token_service.revoke_refresh_token(refresh_token_subject, refresh_token)
    return Response(status_code=HTTPStatus.NO_CONTENT)


def _get_token_subject(token: str, token_service: TokenService):
    try:
        return token_service.get_payload(token).get('sub')
    except (JWTError, ExpiredSignatureError):
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Invalid token')
