from pydantic import BaseModel

from src.utils.exc import ResourceNotFound
from src.infrastructure.db.base import generate_snowflake_id
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface)


class MappingCheck(BaseModel):
    mapping_id: int
    central_catalog_id: int


class MappingCheckUseCase:
    def __init__(
            self, drug_catalog_repository: DrugCatalogRepositoryInterface):
        self.drug_catalog_repository = drug_catalog_repository

    async def execute(self, catalog_to_id: int) -> MappingCheck:
        central_catalog = await self.drug_catalog_repository.get_central()
        if central_catalog is None:
            raise ResourceNotFound("Central catalog not found.")

        related_catalog = await self.drug_catalog_repository.get_by_id(
            catalog_to_id)
        if related_catalog is None:
            raise ResourceNotFound("Related catalog not found.")

        return MappingCheck(
            mapping_id=generate_snowflake_id(),
            central_catalog_id=central_catalog._id
        )
