from sqlalchemy import func, select, update

from src.application.dto.drug_catalog_dto import CountryCode
from src.domain.entities.drug_catalog import DrugCatalog, TaskStatus
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface,
    PagedItems,
)


class IDrugCatalogRepository(DrugCatalogRepositoryInterface):
    async def save(self, drug_catalog: DrugCatalog):
        self.session.add(drug_catalog)
        await self.session.commit()
        await self.session.refresh(drug_catalog)
        return drug_catalog

    async def get_by_id(self, drug_catalog_id: int):
        stmt = select(DrugCatalog).where(DrugCatalog._id == drug_catalog_id)
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def status_update(self, drug_catalog_id: int, status: TaskStatus):
        stmt = (
            update(DrugCatalog)
            .where(DrugCatalog._id == drug_catalog_id)
            .values(status=status)
        )
        if status == "failed":
            stmt = stmt.values(is_central=False)
        await self.session.execute(stmt)

    async def get_central(self):
        stmt = select(DrugCatalog).where(DrugCatalog.is_central.is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_total_count(self, name_filter: str = None) -> int:
        count_stmt = select(func.count(DrugCatalog._id))
        if name_filter:
            count_stmt = count_stmt.where(
                DrugCatalog.name.ilike(f"%{name_filter}%"))
        return await self.session.scalar(count_stmt)

    async def get_first_by_country(self, country: CountryCode):
        stmt = select(DrugCatalog).where(DrugCatalog.country == country)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_paginated(
            self, page: int, page_size: int, name_filter: str = None):
        offset = (page - 1) * page_size
        stmt = (
            select(DrugCatalog)
            .order_by(DrugCatalog.country.asc(), DrugCatalog._id)
            .offset(offset)
            .limit(page_size)
        )

        if name_filter:
            stmt = stmt.where(DrugCatalog.name.ilike(f"%{name_filter}%"))

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        total_count = await self.get_total_count(name_filter)

        return PagedItems[DrugCatalog](
            current_page=page, page_size=page_size,
            total_count=total_count, items=items
        )
