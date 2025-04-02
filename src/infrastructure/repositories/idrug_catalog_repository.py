from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface, PagedItems)


class IDrugCatalogRepository(DrugCatalogRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, drug_catalog: DrugCatalog):
        self.session.add(drug_catalog)
        await self.session.commit()
        await self.session.refresh(drug_catalog)
        return drug_catalog

    async def get_by_id(self, drug_catalog_id: int):
        statement = select(DrugCatalog).where(
            DrugCatalog.id == drug_catalog_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_total_count(self, name_filter: str = None) -> int:
        count_statement = select(DrugCatalog).count()
        if name_filter:
            count_statement = count_statement.where(
                DrugCatalog.name.ilike(f"%{name_filter}%"))
        return await self.session.scalar(count_statement)

    async def get_paginated(self, page: int, page_size: int,
                            name_filter: str = None):
        offset = (page - 1) * page_size
        stmt = select(DrugCatalog).offset(offset).limit(page_size)

        if name_filter:
            stmt = stmt.where(DrugCatalog.name.ilike(f"%{name_filter}%"))

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        total_count = await self.get_total_count(name_filter)

        return PagedItems[DrugCatalog](
            current_page=page,
            page_size=page_size,
            total_count=total_count,
            items=items
        )
