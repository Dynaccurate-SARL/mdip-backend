from typing import List

from src.application.dto.drug_dto import DrugDto
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface, DrugRepositoryInterface)


class GetAllDrugsUseCase:
    def __init__(
            self,
            drug_catalog_repository: DrugCatalogRepositoryInterface,
            drug_repository: DrugRepositoryInterface):
        self.drug_catalog_repository = drug_catalog_repository
        self.drug_repository = drug_repository

    async def execute(self, drug_name_or_code: str) -> List[DrugDto]:
        central_catalog = await self.drug_catalog_repository.get_central()
        drugs = await self.drug_repository.\
            get_all_like_code_or_name_by_catalog_id(
                central_catalog._id, drug_name_or_code)
        return [DrugDto.model_validate(drug) for drug in drugs]
