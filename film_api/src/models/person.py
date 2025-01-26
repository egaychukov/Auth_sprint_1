from pydantic import BaseModel


class Person(BaseModel):
    id: str
    full_name: str


class PersonFilm(BaseModel):
    id: str
    roles: list[str]


class PersonInfo(BaseModel):
    id: str
    full_name: str
    films: list[PersonFilm]
