from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from .desc import desc
from models.genre import Genre
from models.common import ListRequest
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=Genre, description=desc['genres']['get_genre_by_id'])
async def get_genre_by_id(
    genre_id: str,
    genre_service: Annotated[GenreService, Depends(get_genre_service)]
) -> Genre:
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genre not found'
        )
    return Genre(**genre.model_dump())


@router.get('/', response_model=list[Genre], description=desc['genres']['get_genres'])
async def get_genres(
    request: Annotated[ListRequest, Query()],
    genre_service: Annotated[GenreService, Depends(get_genre_service)]
) -> list[Genre]:
    if request.sort and not genre_service.validate_request(request):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='invalid sort parameter'
        )
    genres = await genre_service.get_genres(request)
    return [Genre(**genre.model_dump()) for genre in genres] if genres else []