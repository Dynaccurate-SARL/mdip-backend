from src.application.dto.drug_catalog_dto import (
    DrugCatalogCreateDto, DrugCatalogCreatedDto)
from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface)
from src.infrastructure.services.confidential_ledger.contract import Ledger, TransactionData
from src.utils.checksum import dict_hash, file_checksum


class DrugCatalogCreateUseCase:
    def __init__(self,
                 drug_catalog_repository: DrugCatalogRepositoryInterface,
                 ledger_service: Ledger):
        self.drug_catalog_repository = drug_catalog_repository
        self.ledger_service = ledger_service

    async def execute(
            self, data: DrugCatalogCreateDto) -> DrugCatalogCreatedDto:
        # Create the drug catalog
        drug_catalog = DrugCatalog(
            name=data.name,
            country=data.country,
            version=data.version,
            notes=data.notes,
        )
        drug_catalog = await self.drug_catalog_repository.save(drug_catalog)

        # Send the drug catalog to the ledger
        transaction_data = TransactionData(
            entity_name=DrugCatalog,
            entity_id=drug_catalog.id,
            status='created',
            filename=data.file.filename,
            file_checksum=file_checksum(data.file),
            catatag_hash=dict_hash({
                'id': drug_catalog.id,
                'name': drug_catalog.name,
                'country': drug_catalog.country,
                'version': drug_catalog.version,
                'notes': drug_catalog.notes,
            })
        )
        transaction = await self.ledger_service.insert_transaction(
            transaction_data)

        result = DrugCatalogCreatedDto.model_validate(drug_catalog)
        result.transaction_id = transaction.transaction_id
        return result
