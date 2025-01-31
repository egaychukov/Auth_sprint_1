from typing import Union, Any, Annotated
from datetime import datetime, timedelta

from jose import jwt
from fastapi import Depends

from core.config import settings
from services.token_storage import TokenStorageService, get_token_storage_service


class TokenService:
    def __init__(self, token_storage_service: TokenStorageService):
        self.token_storage_service = token_storage_service

    def create_access_token(self, subject: Union[str, Any]) -> str:
        return self._create_jwt_token(
            subject,
            settings.access_token_expire_minutes
        )

    def create_refresh_token(self, subject: str) -> str:
        token = self._create_jwt_token(
            subject,
            settings.refresh_token_expire_minutes
        )
        self.token_storage_service.add_refresh_token(
            self._get_storage_key(subject, token),
            token
        )
        return token

    def _create_jwt_token(self, subject: Union[str, Any], expires_delta: int) -> str:
        expires_delta = datetime.now() + timedelta(minutes=expires_delta)
        return jwt.encode(
            {"exp": expires_delta, "sub": str(subject)},
            settings.jwt_secret_key,
            settings.jwt_sign_algorithm
        )

    def revoke_access_token(self, subject: str, token: str) -> None:
        self.token_storage_service.add_access_token(
            self._get_storage_key(subject, token),
            token
        )

    def revoke_refresh_token(self, subject: str, token: str) -> None:
        self.token_storage_service.remove_token(
            self._get_storage_key(subject, token)
        )

    def get_payload(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            settings.jwt_sign_algorithm
        )

    def is_access_token_revoked(self, subject: str, token: str) -> bool:
        return self._exists(subject, token)

    def is_refresh_token_revoked(self, subject, token: str) -> bool:
        return not self._exists(subject, token)

    def _exists(self, subject: str, token: str) -> bool:
        token = self.token_storage_service.get_token(
            self._get_storage_key(subject, token)
        )
        return bool(token)

    def _get_storage_key(self, subject: str, token: str):
        return f'{subject}_{token}'


def get_token_service(
    token_storage_service: Annotated[TokenStorageService, Depends(get_token_storage_service)]
) -> TokenService:
    return TokenService(token_storage_service)
