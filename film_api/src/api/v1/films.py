from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from .desc import desc
from .models import FilmListRequest
from models.film import FilmInfo, FilmItem
from models.common import ListRequest, SearchRequest
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/search', response_model=list[FilmItem], description=desc['films']['search_films'])
async def search_films(
        request: Annotated[SearchRequest, Query()],
        film_service: Annotated[FilmService, Depends(get_film_service)]
) -> list[FilmItem]:
    films = await film_service.search_films(request)
    return [FilmItem(**film.model_dump()) for film in films] if films else []


@router.get('/{film_id}', response_model=FilmInfo, description=desc['films']['get_film_details'])
async def get_film_details(
        film_id: str,
        film_service: Annotated[FilmService, Depends(get_film_service)]
) -> FilmInfo:
    film = await film_service.get_film_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found'
        )
    return FilmInfo(**film.model_dump())


@router.get('/', response_model=list[FilmItem], description=desc['films']['get_film_list'])
async def get_film_list(
        request: Annotated[FilmListRequest, Query()],
        film_service: Annotated[FilmService, Depends(get_film_service)]
) -> list[FilmItem]:
    request = ListRequest(**request.model_dump(), query=request.genre)
    if request.sort and not film_service.validate_request(request):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='invalid sort parameter'
        )
    films = await film_service.get_film_list(request)
    return [FilmItem(**film.model_dump()) for film in films] if films else []
