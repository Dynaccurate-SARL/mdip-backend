from src.application.dto.mapping import (
    CentralDrugMappingDto,
    MappingDrugDto,
    BaseDrugDto,
)
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface,
    DrugRepositoryInterface,
    MappingRepositoryInterface,
)
from src.utils.exc import ResourceNotFound


class DrugMappingsUseCase:
    def __init__(
        self,
        drug_catalog_repository: DrugCatalogRepositoryInterface,
        drug_repository: DrugRepositoryInterface,
        mapping_repository: MappingRepositoryInterface,
    ):
        self.drug_catalog_repository = drug_catalog_repository
        self.drug_repository = drug_repository
        self.mapping_repository = mapping_repository

    async def execute(self, drug_id: int) -> CentralDrugMappingDto:
        central_catalog = await self.drug_catalog_repository.get_central()
        if not central_catalog:
            raise ResourceNotFound("Central catalog does not exist")

        central_drug = await self.drug_repository.get_by_id(drug_id)
        if not central_drug or central_drug.catalog_id != central_catalog.id:
            raise ResourceNotFound("Drug not found in central catalog")

        mappings = await self.mapping_repository.get_mappings_by_central_drug_id(
            drug_id
        )

        return CentralDrugMappingDto(
            drug=BaseDrugDto(
                id=central_drug.id,
                drug_name=central_drug.drug_name,
                drug_code=central_drug.drug_code,
                properties=central_drug.properties,
                country=central_drug.country,
            ),
            mappings=[
                MappingDrugDto(
                    id=str(mapping.id),
                    drug_name=mapping.drug_name,
                    drug_code=mapping.drug_code,
                    properties=mapping.properties,
                    country=mapping.country,
                )
                for mapping in mappings
            ],
        )
