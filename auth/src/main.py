from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db import sqlalchemy
from api.v1 import auth


database_url: str = 'sqlite+aiosqlite://'

engine = create_async_engine(database_url, echo=True)
sqlalchemy.async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(sqlalchemy.Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)

app.include_router(auth.router, prefix='/auth', tags=['auth'])
