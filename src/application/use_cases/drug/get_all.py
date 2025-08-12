from re import M
from typing import List

from src.application.dto.drug_dto import DrugMappingsCount
from src.domain.entities.drug import Drug
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface, DrugRepositoryInterface)


class GetDrugsUseCase:
    def __init__(
        self,
        drug_catalog_repository: DrugCatalogRepositoryInterface,
        drug_repository: DrugRepositoryInterface
    ):
        self.drug_catalog_repository = drug_catalog_repository
        self.drug_repository = drug_repository

    async def execute(
        self, drug_name_or_code: str, limit: int
    ) -> List[Drug]:
        central_catalog = await self.drug_catalog_repository.get_central()
        if not central_catalog:
            return []

        drugs = await self.drug_repository.\
            get_all_like_code_or_name_by_catalog_id(
                central_catalog._id, drug_name_or_code)
        return [DrugMappingsCount(
            drug_code=drug.drug_code,
            drug_name=drug.drug_name,
            drug_id=drug.id,
            mapping_count=0
        ) for drug in drugs]
