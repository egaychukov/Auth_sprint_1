from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import Depends

from db.sqlalchemy import get_session, Role, UserRoles


class RoleService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_role(self, role_title: str):
        role = Role(title=role_title)
        self.db_session.add(role)
        await self.db_session.commit()
        return role

    async def delete_role(self, role_id: int):
        stmt = delete(Role).filter_by(id=role_id)
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def grant_role(self, user_id: int, role_id: int):
        user_role = UserRoles(user_id=user_id, role_id=role_id)
        self.db_session.add(user_role)
        await self.db_session.commit()
        return user_role

    async def revoke_role(self, user_id: int, role_id: int):
        stmt = delete(UserRoles).filter_by(user_id=user_id, role_id=role_id)
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def has_role(self, user_id: int, role_id: int):
        query = (
            select(UserRoles)
            .filter_by(role_id=role_id, user_id=user_id)
        )
        return bool(await self.db_session.scalar(query))

    async def get_by_id(self, role_id: int):
        query = select(Role).filter_by(id=role_id)
        return await self.db_session.scalar(query)


def get_role_service(
        db_session: Annotated[AsyncSession, Depends(get_session)]
) -> RoleService:
    return RoleService(db_session)
