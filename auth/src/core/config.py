from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    access_token_expire_minutes: int = Field(10, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_expire_minutes: int = Field(60 * 24 * 3, alias='REFRESH_TOKEN_EXPIRE_MINUTES')
    jwt_secret_key: str = Field(..., alias='JWT_SECRET_KEY')
    jwt_sign_algorithm: str = Field(..., alias='JWT_SIGN_ALGORITHM')
    token_storage_host: str = Field('auth-tokens', alias='TOKEN_STORAGE_HOST')
    token_storage_port: int = Field(6379, alias='TOKEN_STORAGE_PORT')


settings = Settings()
