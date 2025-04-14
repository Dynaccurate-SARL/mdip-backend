from src.config.settings import get_config
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


_async_engine = create_async_engine(
    get_config().DATABASE_URL,
    echo=get_config().DATABASE_ECHO,
)

AsyncLocalSession = async_sessionmaker(
    _async_engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with AsyncLocalSession() as session:
        try:
            yield session
        except Exception:
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
