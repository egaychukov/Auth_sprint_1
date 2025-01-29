from pathlib import Path
import json

import pytest
import asyncio
import pytest_asyncio
from redis import Redis
from aiohttp import ClientSession
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from settings import test_settings
from db.sqlalchemy import User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def users():
    with open(Path('/app') / 'testdata' / 'users.json') as raw_users:
        yield [User(**user) for user in json.load(raw_users)]


@pytest_asyncio.fixture(autouse=True, scope='session')
async def db_session():
    engine = create_async_engine(test_settings.get_connection_string(), echo=True)
    session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
def post(aiohttp_session: ClientSession):
    async def inner(api_route: str, body: dict[str, str]):
        async with aiohttp_session.post(api_route, json=body) as response:
            return response.status, await response.json()
    return inner


@pytest_asyncio.fixture(scope='session')
async def aiohttp_session():
    async with ClientSession(test_settings.get_service_url()) as session:
        yield session


@pytest_asyncio.fixture(autouse=True, scope='session')
async def add_users(db_session: AssertionError, users: list[User]):
    db_session.add_all(users)
    await db_session.commit()
    yield
    stmt = delete(User).where(User.login.in_([user.login for user in users]))
    await db_session.execute(stmt)
    await db_session.commit()
