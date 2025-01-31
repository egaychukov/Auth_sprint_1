from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from redis import Redis
from alembic import command
from alembic.config import Config

from db import sqlalchemy, redis
from api.v1 import auth, role
from core.config import settings


engine = create_async_engine(settings.get_connection_string(), echo=True)
sqlalchemy.async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(
        host=settings.token_storage_host,
        port=settings.token_storage_port
    )
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield
    redis.redis.close()


app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)

app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(role.router, prefix='/role', tags=['role'])
