import typer
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from db.sqlalchemy import User, UserRoles, Role
from core.config import settings
import models.role


app = typer.Typer()

engine = create_async_engine(settings.get_connection_string(), echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@app.command(name='setup-roles')
def setup_roles_command():
    async def setup_roles():
        roles_to_add = [Role(title=role.value) for role in models.role.Role]
        async with async_session() as session:
            async with session.begin():
                session.add_all(roles_to_add)
            await session.commit()
    asyncio.run(setup_roles())


@app.command(name='setup-admin')
def setup_admin_command():
    async def setup_user():
        async with async_session() as session:
            async with session.begin():
                admin = User(
                    login=settings.default_admin_login,
                    password=settings.default_admin_password,
                    first_name='admin',
                    last_name='admin'
                )
                session.add(admin)

    async def setup_roles():
        async with async_session() as session:
            async with session.begin():
                admin = await session.scalar(
                    select(User)
                    .filter_by(login=settings.default_admin_login)
                )
                user_roles = []
                for role in (await session.scalars(select(Role))):
                    user_roles.append(
                        UserRoles(user_id=admin.id, role_id=role.id)
                    )
                session.add_all(user_roles)

    async def setup_admin():
        await setup_user()
        await setup_roles()

    asyncio.run(setup_admin())


if __name__ == "__main__":
    app()
