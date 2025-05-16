from src.utils.exc import ConflictErrorCode
from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface)
from src.application.dto.drug_catalog_dto import (
    DrugCatalogCreateDto, DrugCatalogCreatedDto)


class DrugCatalogCreateUseCase:
    def __init__(
            self, drug_catalog_repository: DrugCatalogRepositoryInterface):
        self._drug_catalog_repository = drug_catalog_repository

    async def execute(
            self, data: DrugCatalogCreateDto) -> DrugCatalogCreatedDto:
        if data.is_central:
            # Check if the central drug catalog already exists
            central_catalog = await self._drug_catalog_repository.get_central()
            if central_catalog:
                raise ConflictErrorCode('Central drug catalog already exists.')

        # Create the drug catalog
        drug_catalog = DrugCatalog(
            name=data.name,
            country=data.country,
            version=data.version,
            notes=data.notes,
            is_central=data.is_central
        )
        drug_catalog = await self._drug_catalog_repository.save(drug_catalog)
        return DrugCatalogCreatedDto.model_validate(drug_catalog)
