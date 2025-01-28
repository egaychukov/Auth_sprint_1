from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError

from services.role import RoleService, get_role_service
from services.user import UserService, get_user_service


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post('/create/{role_title}')
async def create_role(
        role_title: str,
        role_service: Annotated[RoleService, Depends(get_role_service)]
):
    try:
        return await role_service.create_role(role_title)
    except IntegrityError:
        raise HTTPException(HTTPStatus.BAD_REQUEST)


@router.delete('/remove/{role_id}')
async def remove_role(
        role_id: int,
        role_service: Annotated[RoleService, Depends(get_role_service)]
):
    if not (await role_service.get_by_id(role_id)):
        raise HTTPException(HTTPStatus.NOT_FOUND)
    try:
        await role_service.delete_role(role_id)
        return Response(status_code=HTTPStatus.NO_CONTENT)
    except IntegrityError:
        raise HTTPException(HTTPStatus.BAD_REQUEST)


@router.post('/assign/{user_id}/{role_id}')
async def grant_role(
        user_id: int,
        role_id: int,
        role_service: Annotated[RoleService, Depends(get_role_service)],
        user_service: Annotated[UserService, Depends(get_user_service)]
):
    if not (await user_service.get_by_id(user_id)):
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User not found')
    if not (await role_service.get_by_id(role_id)):
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Role not found')
    try:
        await role_service.grant_role(user_id, role_id)
        return {'user_id': user_id, 'role_id': role_id}
    except IntegrityError:
        raise HTTPException(HTTPStatus.BAD_REQUEST)


@router.post('/revoke/{user_id}/{role_id}')
async def revoke_role(
        user_id: int,
        role_id: int,
        role_service: Annotated[RoleService, Depends(get_role_service)],
        user_service: Annotated[UserService, Depends(get_user_service)]
):
    if not (await user_service.get_by_id(user_id)):
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User not found')
    if not (await role_service.get_by_id(role_id)):
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Role not found')
    try:
        await role_service.revoke_role(user_id, role_id)
        return Response(status_code=HTTPStatus.NO_CONTENT)
    except IntegrityError:
        raise HTTPException(HTTPStatus.BAD_REQUEST)


@router.get('/belongs/{user_id}/{role_id}')
async def has_role(
        user_id: int,
        role_id: int,
        role_service: Annotated[RoleService, Depends(get_role_service)],
        user_service: Annotated[UserService, Depends(get_user_service)]
):
    if not (await user_service.get_by_id(user_id)):
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User not found')
    if not (await role_service.get_by_id(role_id)):
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Role not found')
    return {'belongs': await role_service.has_role(user_id, role_id)}
