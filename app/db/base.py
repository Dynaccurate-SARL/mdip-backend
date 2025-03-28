from typing import Self

from sqlalchemy import update, delete

from .engine import get_async_session, Base


# Base Mixin object.
class BaseMixin:
    __mapper_args__ = {'always_refresh': True}

    @property
    def metadatetime(self):
        return self

    async def insert(self, refresh: bool = True) -> Self:
        """
        Use only for insert operation
        """
        async with get_async_session() as session:
            session.add(self)
            await session.commit()
            if refresh:
                await session.refresh(self)
                return self

    async def update(self, **kwargs) -> Self:
        """
        Use only for update operation
        """
        async with get_async_session() as session:
            # set the new values
            stmt = update(self.__class__).where(
                self.__class__.id == self.id).values(**kwargs)
            # commit the modifications
            await session.execute(stmt)
            await session.commit()
            # updates current object
            for key, value in kwargs.items():
                setattr(self, key, value)
            return self

    async def delete(self) -> Self:
        """
        Use only for delete operation
        """
        async with get_async_session() as session:
            stmt = delete(self.__class__).where(self.__class__.id == self.id)
            await session.execute(stmt)
            await session.commit()
            return self
