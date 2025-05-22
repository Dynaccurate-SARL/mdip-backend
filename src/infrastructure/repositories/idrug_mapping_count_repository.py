from typing import List
from sqlalchemy import select

from src.domain.entities.drug_mapping_count_view import DrugMappingCountView
from src.infrastructure.repositories.contract import DrugMappingCountViewInterface


class IDrugMappingCountViewInterface(DrugMappingCountViewInterface):
    async def get_all_like_code_or_name(
        self, name_or_code_filter: str = "", limit: int = 0
    ) -> List[DrugMappingCountView]:
        stmt = select(DrugMappingCountView)
        if name_or_code_filter:
            stmt = stmt.where(
                (DrugMappingCountView.drug_name.ilike(f"%{name_or_code_filter}%"))
                | (DrugMappingCountView.drug_code.ilike(f"%{name_or_code_filter}%"))
            )
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        drugs = result.scalars().all()
        return drugs
