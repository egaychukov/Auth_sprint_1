from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import check_password_hash, generate_password_hash


Base = declarative_base()
async_session: sessionmaker = None


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    login: Mapped[str] = mapped_column(unique=True)
    pass_hash: Mapped[str]

    roles = relationship('Role', back_populates='users', secondary='user_roles')

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.pass_hash = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.pass_hash, password)


class UserRoles(Base):
    __tablename__ = 'user_roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'))


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)

    users = relationship('User', back_populates='roles', secondary='user_roles', cascade='all, delete')


async def get_session():
    async with async_session() as session:
        yield session
