from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from .desc import desc
from models.film import FilmItem
from models.person import PersonInfo
from models.common import SearchRequest
from services.person import PersonService, get_person_service
from auth.auth import security_jwt


router = APIRouter()


@router.get('/search', response_model=list[PersonInfo], description=desc['persons']['search_persons'])
async def search_persons(
        request: Annotated[SearchRequest, Query()],
        person_service: Annotated[PersonService, Depends(get_person_service)],
        _: Annotated[dict, Depends(security_jwt)]
) -> list[PersonInfo]:
    people = await person_service.search_persons(request)
    if not people:
        return []
    people_roles = []
    for person in people:
        roles = await person_service.get_person_film_roles(person.id)
        people_roles.append(PersonInfo(**person.model_dump(), films=(roles if roles else [])))
    return people_roles


@router.get('/{person_id}/film', response_model=list[FilmItem], description=desc['persons']['get_person_films'])
async def get_person_films(
        person_id: str,
        person_service: Annotated[PersonService, Depends(get_person_service)],
        _: Annotated[dict, Depends(security_jwt)]
) -> list[FilmItem]:
    films = await person_service.get_person_films(person_id)
    return [FilmItem(**film.model_dump()) for film in films] if films else []


@router.get('/{person_id}', response_model=PersonInfo, description=desc['persons']['get_person_by_id'])
async def get_person_by_id(
        person_id: str,
        person_service: Annotated[PersonService, Depends(get_person_service)],
     _: Annotated[dict, Depends(security_jwt)]
) -> PersonInfo:
    person = await person_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='no person found by id provided'
        )
    person_roles = await person_service.get_person_film_roles(person_id)
    return PersonInfo(**person.model_dump(), films=(person_roles if person_roles else []))
