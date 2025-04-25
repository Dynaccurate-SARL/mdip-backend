from fastapi import UploadFile
from pydantic import BaseModel

from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface)
from src.infrastructure.services.confidential_ledger.contract import (
    Ledger, TransactionData)
from src.utils.checksum import file_checksum
from src.utils.exc import ResourceNotFound


class MappingCreate(BaseModel):
    central_catalog_id: int
    catalog_to_id: int


class MappingCreateUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface,
                 ledger_service: Ledger):
        self.drug_catalog_repository = drug_catalog_repository
        self.ledger_service = ledger_service

    async def execute(self, catalog_to_id: int, file: UploadFile):
        central_catalog = await self.drug_catalog_repository.get_central()
        if central_catalog is None:
            raise ResourceNotFound("Central catalog not found.")
        
        related_catalog = await self.drug_catalog_repository.get_by_id(
            catalog_to_id)
        if related_catalog is None:
            raise ResourceNotFound("Related catalog not found.")

        transaction_data = TransactionData(
            entity_name=DrugCatalog.__tablename__,
            entity_id=catalog_to_id,
            status='created',
            data={
                'type': 'mapping_import',
                'filename': file.filename,
                'file_checksum': file_checksum(file),
                'catalog_central_id': central_catalog._id,
                'catalog_to_id': catalog_to_id,
            }
        )
        await self.ledger_service.insert_transaction(transaction_data)

        return MappingCreate(
            central_catalog_id=central_catalog._id,
            catalog_to_id=catalog_to_id
        )
