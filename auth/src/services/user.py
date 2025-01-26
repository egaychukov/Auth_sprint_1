from typing import Annotated, Coroutine, Any

from fastapi import Depends
from sqlalchemy import select

from db.sqlalchemy import get_session, AsyncSession, User
from models.user import UserCreateRequest


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, request: UserCreateRequest):
        new_user = User(**request.model_dump())
        self.db_session.add(new_user)
        await self.db_session.commit()
        return new_user

    async def get_by_login(self, login: str):
        query = select(User).filter_by(login=login)
        return await self.db_session.scalar(query)

    async def check_password(self, user_id, password: str):
        query = select(User).filter_by(id=user_id)
        user = await self.db_session.scalar(query)
        if not user:
            return False
        return user.check_password(password)


def get_user_service(
        db_session: Annotated[AsyncSession, Depends(get_session)]):
    return UserService(db_session)
