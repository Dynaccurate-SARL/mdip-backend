from src.application.dto.drug_dto import DrugDto, DrugPaginatedDto
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface, DrugRepositoryInterface)


class GetPaginatedDrugUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface,
                 drug_repository: DrugRepositoryInterface):
        self.drug_catalog_repository = drug_catalog_repository
        self.drug_repository = drug_repository

    async def execute(self, page: int, page_size: int,
                      name_or_code_filter: str) -> DrugPaginatedDto:
        central_catalog = await self.drug_catalog_repository.get_central()
        result = await self.drug_repository.get_paginated_by_catalog_id(
            page, page_size, central_catalog._id, name_or_code_filter
        )
        items = [DrugDto.model_validate(drug) for drug in result.items]
        return DrugPaginatedDto(
            data=items,
            page=result.current_page,
            limit=result.page_size,
            total=result.total_count
        )
