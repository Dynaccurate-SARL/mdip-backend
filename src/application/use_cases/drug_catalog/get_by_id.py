from src.application.dto.drug_catalog_dto import DrugCatalogDto
from src.infrastructure.repositories.contract import DrugCatalogRepositoryInterface


class GetDrugCatalogByIdUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface):
        self.drug_catalog_repository = drug_catalog_repository

    async def execute(self, drug_catalog_id: int) -> DrugCatalogDto | None:
        drug_catalog = await self.drug_catalog_repository.get_by_id(
            drug_catalog_id)
        if drug_catalog:
            result = DrugCatalogDto.model_validate(drug_catalog)
            return result
        return None