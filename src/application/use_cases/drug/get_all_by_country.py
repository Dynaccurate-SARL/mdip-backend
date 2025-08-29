from typing import List, Literal

from src.application.dto.drug_dto import DrugMappingsCount
from src.domain.entities.drug import Drug
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface, DrugRepositoryInterface)
from src.application.dto.drug_catalog_dto import _CountryCode


DrugCountry = _CountryCode | Literal["EU"]


class GetDrugsByCountryUseCase:
    def __init__(
        self,
        drug_catalog_repository: DrugCatalogRepositoryInterface,
        drug_repository: DrugRepositoryInterface
    ):
        self.drug_catalog_repository = drug_catalog_repository
        self.drug_repository = drug_repository

    async def execute(
            self, country: DrugCountry, drug_name_or_code: str) -> List[Drug]:
        catalog = await self.drug_catalog_repository.get_first_by_country(
            country)
        if not catalog:
            return []

        drugs = await self.drug_repository.\
            get_all_like_code_or_name_by_catalog_id(
                catalog._id, drug_name_or_code)
        return [DrugMappingsCount(
            drug_code=drug.drug_code,
            drug_name=drug.drug_name,
            drug_id=drug.id
        ) for drug in drugs]
