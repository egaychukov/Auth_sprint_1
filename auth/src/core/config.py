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
    default_admin_login: str = Field(..., alias='DEFAULT_ADMIN_LOGIN')
    default_admin_password: str = Field(..., alias='DEFAULT_ADMIN_PASSWORD')
    database_user: str = Field(..., alias='POSTGRES_USER')
    database_password: str = Field(..., alias='POSTGRES_PASSWORD')
    database_name: str = Field(..., alias='POSTGRES_DB')
    database_host: str = Field('database', alias='POSTGRES_HOST')
    database_port: int = Field(5432, alias='POSTGRES_PORT')

    def get_connection_string(self):
        return f'postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}'


settings = Settings()
