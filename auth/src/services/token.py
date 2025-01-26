from typing import Union, Any
from datetime import datetime, timedelta

from jose import jwt

from core.config import settings


class TokenService:
    def create_access_token(self, subject: Union[str, Any]) -> str:
        return self._create_jwt_token(
            subject,
            settings.access_token_expire_minutes
        )

    def create_refresh_token(self, subject: Union[str, Any]) -> str:
        return self._create_jwt_token(
            subject,
            settings.refresh_token_expire_minutes
        )

    def _create_jwt_token(self, subject: Union[str, Any], expires_delta: int) -> str:
        expires_delta = datetime.now() + timedelta(minutes=expires_delta)
        return jwt.encode(
            {"exp": expires_delta, "sub": str(subject)},
            settings.jwt_secret_key,
            settings.jwt_sign_algorithm
        )


def get_token_service():
    return TokenService()
