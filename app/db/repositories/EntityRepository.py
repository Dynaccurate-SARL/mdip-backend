from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from typing import List

from app.modules.entity.schemas import EntityTypeEnum

from ..engine import get_async_session
from .models import Entity


async def get_all() -> List[Entity]:
    async with get_async_session() as session:
        stmt = select(Entity).where(Entity.is_active == True)
        result = await session.execute(stmt)
    return result.scalars().all()


async def get_by_id(id: int) -> Entity:
    async with get_async_session() as session:
        stmt = select(Entity).where(Entity.id == id, Entity.is_active == True)
        stmt = stmt.options(selectinload(Entity.reg_transactions))
        result = await session.execute(stmt)
    return result.scalars().one_or_none()


async def get_by_type_and_name(entity_type: EntityTypeEnum, name: str = "") -> List[Entity]:
    async with get_async_session() as session:
        stmt = select(Entity).where(Entity.is_active == True).where(
            Entity.entity_type == entity_type.value).where(or_(Entity.destination.ilike(f'%{name}%'),
                                                               Entity.origin.ilike(f'%{name}%')))
        result = await session.execute(stmt)
    return result.scalars().all()
