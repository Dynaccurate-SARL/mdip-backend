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




        # # Send the drug catalog to the ledger
        # transaction_data = CatalogTransactionData(
        #     status='created',
        #     filename=data.file.filename,
        #     file_checksum=file_checksum(data.file),
        #     catalog_id=drug_catalog.id,
        #     created_at=datetime.now(timezone.utc).isoformat(),
        #     created_at_tz='UTC'
        # )
        # ledger_transaction = self._ledger_service.insert_transaction(
        #     transaction_data)
        # transaction = CatalogTransaction(
        #     catalog_id=drug_catalog._id,
        #     payload=transaction_data,
        #     transaction_id=ledger_transaction.transaction_id
        # )
        # await self._transaction_repository.save(transaction)

        # result = DrugCatalogCreatedDto.model_validate(drug_catalog)
        # return UseCaseResult(result=result, transaction_data=transaction_data)
