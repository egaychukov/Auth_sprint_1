from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    es_host: str = Field('elasticsearch', alias='ELASTIC_HOST')
    es_port: int = Field(9200, alias='ELASTIC_PORT')
    es_scheme: str = Field('http', alias='ELASTIC_SCHEME')
    es_films_index: str = Field('movies', alias='ELASTIC_FILMS_INDEX')
    es_genres_index: str = Field('genre', alias='ELASTIC_GENRES_INDEX')
    es_person_index: str = Field('person', alias='ELASTIC_PERSON_INDEX')
    redis_host: str = Field('redis', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')
    service_host: str = Field('film-api', alias='SERVICE_URL')
    service_port: int = Field(8000, alias='SERVICE_PORT')

    def get_es_url(self):
        return f'{self.es_scheme}://{self.es_host}:{self.es_port}'

    def get_service_url(self):
        return f'http://{self.service_host}:{self.service_port}'


test_settings = TestSettings()
