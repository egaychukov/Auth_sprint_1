from pathlib import Path
import json
from typing import Optional
from http import HTTPStatus

import pytest
import asyncio
import pytest_asyncio
from redis import Redis
from aiohttp import ClientSession
from sqlalchemy import delete, select
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
    async def inner(api_route: str, body: dict[str, str], headers: Optional[dict[str, str]] = None):
        async with aiohttp_session.post(api_route, json=body, headers=headers) as response:
            if response.status == HTTPStatus.NO_CONTENT:
                return response.status, None
            return response.status, await response.json()
    return inner


@pytest_asyncio.fixture(scope='session')
async def aiohttp_session():
    async with ClientSession(test_settings.get_service_url()) as session:
        yield session


@pytest_asyncio.fixture(autouse=True, scope='session')
async def setup_users(db_session: AsyncSession, users: list[User]):
    db_session.add_all(users)
    await db_session.commit()
    yield
    await db_session.execute(delete(User))
    await db_session.commit()


@pytest_asyncio.fixture(scope='session')
def get_current_users(db_session: AsyncSession):
    async def inner():
        result = await db_session.scalars(select(User))
        return result.all()
    return inner


@pytest.fixture(scope='session')
def redis():
    redis = Redis(
        test_settings.token_storage_host,
        test_settings.token_storage_port
    )
    yield redis
    redis.close()


@pytest.fixture(scope='session')
def token_exists(redis: Redis):
    def inner(subject: str, token: str):
        return redis.exists(f'{subject}_{token}')
    return inner
