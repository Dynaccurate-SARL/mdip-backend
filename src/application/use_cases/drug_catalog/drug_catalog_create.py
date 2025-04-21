from src.application.dto.drug_catalog_dto import (
    DrugCatalogCreateDto, DrugCatalogCreatedDto)
from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface)
from src.infrastructure.services.confidential_ledger.contract import (
    Ledger, TransactionData)
from src.utils.checksum import file_checksum
from src.utils.exc import ConflictErrorCode


class DrugCatalogCreateUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface,
                 ledger_service: Ledger):
        self.drug_catalog_repository = drug_catalog_repository
        self.ledger_service = ledger_service

    async def execute(
            self, data: DrugCatalogCreateDto) -> DrugCatalogCreatedDto:
        if data.is_central:
            # Check if the central drug catalog already exists
            has_central = await self.drug_catalog_repository.\
                exists_central_catalog()
            if has_central:
                raise ConflictErrorCode('Central drug catalog already exists.')

        # Create the drug catalog
        drug_catalog = DrugCatalog(
            name=data.name,
            country=data.country,
            version=data.version,
            notes=data.notes,
            is_central=data.is_central
        )
        drug_catalog = await self.drug_catalog_repository.save(drug_catalog)

        # Send the drug catalog to the ledger
        transaction_data = TransactionData(
            # Entity transacton reference
            entity_name=DrugCatalog,
            entity_id=drug_catalog._id,
            # Data that is sent to the ledger
            status='created',
            data={
                'filename': data.file.filename,
                'file_checksum': file_checksum(data.file),
                'catalog': {
                    'id': drug_catalog.id,
                    'name': drug_catalog.name,
                    'country': drug_catalog.country,
                    'version': drug_catalog.version,
                    'notes': drug_catalog.notes,
                    'is_central': 'yes' if drug_catalog.is_central else 'no',
                }
            }
        )
        transaction = await self.ledger_service.insert_transaction(
            transaction_data)

        result = DrugCatalogCreatedDto.model_validate(drug_catalog)
        result.transaction_id = transaction.transaction_id
        return result
