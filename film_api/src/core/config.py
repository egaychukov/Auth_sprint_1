from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    project_name: str = 'movies'
    redis_host: str = Field(..., alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')
    elastic_host: str = Field(..., alias='ELASTIC_HOST')
    elastic_port: int = Field(9200, alias='ELASTIC_PORT')
    elastic_scheme: str = Field('http', alias='ELASTIC_SCHEME')
    default_cache_expiry_in_seconds: int = Field(30, alias='CACHE_EXPIRY_IN_SECONDS')
    es_load_batch_size: int = Field(20, alias='ES_LOAD_BATCH_SIZE')


settings = Settings()
