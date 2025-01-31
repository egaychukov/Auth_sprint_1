from pydantic import BaseModel, Field


class Person(BaseModel):
    id: str
    name: str


class FilmInfo(BaseModel):
    id: str
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list[str]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]

    class Config:
        extra = 'ignore'


class FilmItem(BaseModel):
    id: str
    title: str
    imdb_rating: float | None


class FilmListRequest(BaseModel):
    page_number: int | None = Field(None, ge=0)
    page_size: int | None = Field(None, gt=0)
    sort: str | None = Field(None, pattern=r'^[-+][a-zA-Z_]+$')
    genre: str | None = None
