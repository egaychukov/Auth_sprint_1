from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    access_token_expire_minutes: int = 10
    refresh_token_expire_minutes: int = 60 * 24 * 3
    jwt_secret_key: str = ''
    jwt_sign_algorithm: str = ''


settings = Settings()
