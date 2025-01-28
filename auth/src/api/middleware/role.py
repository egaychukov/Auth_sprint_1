from http import HTTPStatus

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from services.user import UserService
from services.role import RoleService


class CheckEntitiesMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, user_service: UserService, role_service: RoleService):
        super().__init__(app)
        self.user_service = user_service
        self.role_service = role_service

    async def dispatch(self, request: Request, call_next):
        user_id = request.path_params['user_id']
        role_id = request.path_params['role_id']

        if not (await self.user_service.get_by_id(user_id)):
            return Response(status_code=HTTPStatus.NOT_FOUND, content='User not found')
        if not (await self.role_service.get_by_id(role_id)):
            return Response(status_code=HTTPStatus.NOT_FOUND, content='Role not found')

        response = await call_next(request)
        return response
