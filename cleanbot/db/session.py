"""Database engine and session management."""
from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cleanbot.core.settings import settings
from cleanbot.db import models

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_pass.get_secret_value()}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession)


async def create_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def drop_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)


@asynccontextmanager
async def get_async_session():
    async with session_maker() as session:
        yield session


async def get_async_session_dependency() -> AsyncSession:
    async with session_maker() as session:
        yield session
