from src.infrastructure.repositories.contract import DrugCatalogRepositoryInterface
from src.application.dto.drug_catalog_dto import DrugCatalogDto, DrugCatalogPaginatedDto


class GetPaginatedDrugCatalogUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface):
        self.drug_catalog_repository = drug_catalog_repository

    async def execute(
        self, page: int, page_size: int, name: str
    ) -> DrugCatalogPaginatedDto:
        result = await self.drug_catalog_repository.get_paginated(page, page_size, name)
        items = [DrugCatalogDto.model_validate(drug) for drug in result.items]
        return DrugCatalogPaginatedDto(
            data=items,
            page=result.current_page,
            limit=result.page_size,
            total=result.total_count,
        )
