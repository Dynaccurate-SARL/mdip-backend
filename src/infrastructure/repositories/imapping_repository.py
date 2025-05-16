from typing import List
from sqlalchemy import delete, func
from sqlalchemy.future import select

from src.domain.entities.drug import Drug
from src.domain.entities.drug_catalog import DrugCatalog
from src.domain.entities.drug_mapping import DrugMapping
from src.infrastructure.repositories.contract import (
    CentralDrugMapping, MappingRepositoryInterface)


class IMappingRepository(MappingRepositoryInterface):

    async def save(self, mapping: DrugMapping) -> DrugMapping:
        self.session.add(mapping)
        await self.session.commit()
        await self.session.refresh(mapping)
        return mapping

    async def get_total_count(self) -> int:
        count_statement = select(func.count(DrugMapping._drug_id))
        return await self.session.scalar(count_statement)

    async def get_mappings_by_central_drug_id(
            self, central_drug_id: int) -> List[CentralDrugMapping]:

        stmt = (
            select(
                Drug._id.label("id"),
                Drug.drug_code.label("drug_code"),
                Drug.drug_name.label("drug_name"),
                DrugCatalog.country.label("country"),
                Drug.properties.label("properties")
            )
            .select_from(DrugMapping)
            .join(Drug, Drug._id == DrugMapping._related_drug_id)
            .join(DrugCatalog, Drug._catalog_id == DrugCatalog._id)
            .where(DrugMapping._drug_id == central_drug_id)
        )

        result = await self.session.execute(stmt)
        rows = result.fetchall()
        return [
            CentralDrugMapping(
                id=row.id,
                drug_code=row.drug_code,
                drug_name=row.drug_name,
                properties=row.properties,
                country=row.country,
            ) for row in rows
        ]

    async def delete_all_by_mapping_id(self, mapping_id: int):
        query = delete(DrugMapping).where(
            DrugMapping._mapping_id == mapping_id)
        await self.session.execute(query)
        await self.session.commit()
