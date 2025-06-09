from typing import List
from sqlalchemy import delete, func
from sqlalchemy.future import select

from src.domain.entities import Drug
from src.infrastructure.repositories.contract import DrugRepositoryInterface, PagedItems


class IDrugRepository(DrugRepositoryInterface):
    async def save(self, drug: Drug) -> Drug:
        self.session.add(drug)
        await self.session.commit()
        await self.session.refresh(drug)
        return drug

    async def get_by_id(self, id: int):
        query = select(Drug).where(Drug._id == id)
        result = await self.session.execute(query)
        drug = result.scalar_one_or_none()
        return drug

    async def delete_all_by_catalog_id(self, catalog_id: int):
        query = delete(Drug).where(Drug._catalog_id == catalog_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_by_drug_code_on_catalog_id(self, catalog_id: int, drug_code: str):
        query = select(Drug).where(
            (Drug.drug_code == drug_code) & (Drug._catalog_id == catalog_id)
        )
        result = await self.session.execute(query)
        drug = result.scalar_one_or_none()
        return drug

    async def get_all_like_code_or_name_by_catalog_id(
        self, catalog_id: int, name_or_code: str
    ) -> List[Drug]:
        query = (
            select(Drug)
            .where(Drug._catalog_id == catalog_id)
            .order_by(Drug._id)
            .where(
                (Drug.drug_name.ilike(f"%{name_or_code}%"))
                | (Drug.drug_code.ilike(f"%{name_or_code}%"))
            )
        )
        result = await self.session.execute(query)
        drugs = result.scalars().all()
        return drugs

    async def get_total_count(
        self, drug_catalog_id: int, name_or_code_filter: str = None
    ) -> int:
        count_statement = select(func.count(Drug._id)).where(
            Drug._catalog_id == drug_catalog_id
        )
        if name_or_code_filter:
            count_statement = count_statement.where(
                (Drug.drug_name.ilike(f"%{name_or_code_filter}%"))
                | (Drug.drug_name.ilike(f"%{name_or_code_filter}%"))
            )
        return await self.session.scalar(count_statement)

    async def get_paginated_by_catalog_id(
        self,
        page: int,
        page_size: int,
        drug_catalog_id: int,
        name_or_code_filter: str = None,
    ):
        offset = (page - 1) * page_size
        stmt = (
            select(Drug)
            .where(Drug._catalog_id == drug_catalog_id)
            .order_by(Drug._id)
            .offset(offset)
            .limit(page_size)
        )

        if name_or_code_filter:
            stmt = stmt.where(
                (Drug.drug_name.ilike(f"%{name_or_code_filter}%"))
                | (Drug.drug_code.ilike(f"%{name_or_code_filter}%"))
            )

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        total_count = await self.get_total_count(drug_catalog_id, name_or_code_filter)

        return PagedItems[Drug](
            current_page=page, page_size=page_size, total_count=total_count, items=items
        )
