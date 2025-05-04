from typing import List

from src.domain.entities.drug_mapping_count_view import DrugMappingCountView
from src.infrastructure.repositories.contract import DrugMappingCountViewInterface


class GetDrugsUseCase:
    def __init__(
            self, drug_mapping_count_repository: DrugMappingCountViewInterface):
        self.drug_mapping_count_repository = drug_mapping_count_repository

    async def execute(self, drug_name_or_code: str, limit: int) -> List[DrugMappingCountView]:
        drugs = await self.drug_mapping_count_repository.\
            get_all_like_code_or_name(drug_name_or_code, limit)
        return drugs
