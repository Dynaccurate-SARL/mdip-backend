from sqlalchemy import select

from typing import List

from ..engine import get_async_session
from .models import Transaction


async def get_all_by_entity_id(entity_id: int) -> List[Transaction]:
    async with get_async_session() as session:
        stmt = select(Transaction).where(Transaction._entity_id == entity_id)
        result = await session.execute(stmt)
    return result.scalars().all()


async def get_by_id(id: str) -> Transaction | None:
    async with get_async_session() as session:
        stmt = select(Transaction).where(Transaction.id == id)
        result = await session.execute(stmt)
    return result.scalars().one_or_none()
