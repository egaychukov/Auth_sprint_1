from pydantic import BaseModel


class FilmItem(BaseModel):
    id: str
    title: str
    imdb_rating: float | None


class CastMember(BaseModel):
    id: str
    name: str


class FilmInfo(BaseModel):
    id: str
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list[str]
    actors: list[CastMember]
    writers: list[CastMember]
    directors: list[CastMember]

    class Config:
        extra = 'ignore'
