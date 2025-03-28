# Standard Imports
import logging as log
from contextlib import asynccontextmanager
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..config import get_config


_async_engine = create_async_engine(
    get_config().ASYNC_DATABASE_URL,
    echo=False,
)

AsyncLocalSession = async_sessionmaker(
    _async_engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def get_async_session():
    session: AsyncSession = AsyncLocalSession()
    try:
        yield session
    except Exception as e:
        log.critical(e)
        await session.rollback()
        raise
    finally:
        await session.close()


async def create_all():
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
