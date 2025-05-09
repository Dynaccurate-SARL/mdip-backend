from src.application.dto.drug_dto import DrugDto, DrugPaginatedDto
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface, DrugRepositoryInterface)
from src.utils.exc import ResourceNotFound


class GetPaginatedDrugsUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface,
                 drug_repository: DrugRepositoryInterface):
        self.drug_catalog_repository = drug_catalog_repository
        self.drug_repository = drug_repository

    async def execute(
            self, page: int, page_size: int, name_or_code_filter: str, 
            catalog_id: int = None) -> DrugPaginatedDto:
        if catalog_id:
            catalog = await self.drug_catalog_repository.get_by_id(catalog_id)
        else:
            catalog = await self.drug_catalog_repository.get_central()
        if not catalog:
            raise ResourceNotFound("Catalog not found")
        
        result = await self.drug_repository.get_paginated_by_catalog_id(
            page, page_size, catalog._id, name_or_code_filter
        )
        items = [DrugDto.model_validate(drug) for drug in result.items]
        return DrugPaginatedDto(
            data=items,
            page=result.current_page,
            limit=result.page_size,
            total=result.total_count
        )
