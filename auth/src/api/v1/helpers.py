from http import HTTPStatus
from typing import Annotated

import aiohttp
from jose import jwt
from jose.exceptions import JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/register/')


def get_user_id(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        return jwt.decode(
            token,
            key=settings.jwt_secret_key,
            algorithms=settings.jwt_sign_algorithm
        ).get('sub')
    except JWTError:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)


def require(role: str):
    async def wrapper(user_id: Annotated[str, Depends(get_user_id)]):
        url = f'http://auth:8000/role/belongs/{user_id}/{role}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status >= HTTPStatus.BAD_REQUEST:
                    raise HTTPException(HTTPStatus.UNAUTHORIZED)
                response = await response.json()
                if not response['belongs']:
                    raise HTTPException(HTTPStatus.UNAUTHORIZED)
    return wrapper
