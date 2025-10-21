from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.testing.plugin.plugin_base import logging

from config_reader import config
from database.models import Base


engine = create_async_engine(config.build_database_url(), echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@asynccontextmanager
async def get_async_session():
    async with session_maker() as session:
        yield session


async def get_async_session_dependency() -> AsyncSession:
    async with session_maker() as session:
        yield session