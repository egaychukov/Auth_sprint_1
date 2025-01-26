from sqlalchemy.orm import Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash, generate_password_hash

Base = declarative_base()
async_session: sessionmaker = None


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    login: Mapped[str] = mapped_column(unique=True)
    pass_hash: Mapped[str]

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.pass_hash = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.pass_hash, password)


async def get_session():
    async with async_session() as session:
        yield session
