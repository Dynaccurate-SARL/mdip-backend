import logging as log

from src.domain.entities.drug_catalog import DrugCatalog, ImportStatus
from src.domain.entities.drug_mapping import DrugMapping
from src.domain.entities.ltransactions import MappingTransaction, MappingTransactionData
from src.infrastructure.repositories.contract import DrugCatalogRepositoryInterface, DrugRepositoryInterface, MappingRepositoryInterface, MappingTransactionRepositoryInterface
from src.infrastructure.services.confidential_ledger.contract import LedgerInterface
from src.infrastructure.services.pandas_parser.mapping.parse import MappingParser
from src.utils.exc import ResourceNotFound


class MappingImportUseCase:
    def __init__(
            self, drug_repository: DrugRepositoryInterface,
            transaction_repository: MappingTransactionRepositoryInterface,
            mapping_repository: MappingRepositoryInterface,
            transaction_data: MappingTransactionData,
            ledger_service: LedgerInterface, mapping_parser: MappingParser,
            central_catalog_id: int, catalog_to_id: int):
        self._drug_repository = drug_repository
        self._transaction_repository = transaction_repository
        self._mapping_repository = mapping_repository
        self._transaction_data = transaction_data
        self._ledger_service = ledger_service
        self._mapping_parser = mapping_parser
        self._central_catalog_id = central_catalog_id
        self._catalog_to_id = catalog_to_id

    async def _save_mappings(self, mappings: list[DrugMapping]):
        for mapping in mappings:
            central_catalog_drug = await self._drug_repository.\
                get_by_drug_code_on_catalog_id(
                    self._central_catalog_id, mapping.drug_code)
            if central_catalog_drug:
                related_catalog_drug = await self._drug_repository.\
                    get_by_drug_code_on_catalog_id(
                        self._catalog_to_id, mapping.related_drug_code)
                try:
                    mapping = DrugMapping(
                        drug_id=central_catalog_drug._id,
                        related_drug_id=related_catalog_drug._id)
                    await self._mapping_repository.save(mapping)
                except Exception:
                    pass

    async def _update_status(self, status: ImportStatus):
        self._transaction_data['status'] = status
        ledger_transaction = self._ledger_service.insert_transaction(
            self._transaction_data)

        transaction = MappingTransaction(
            catalog_id=self._catalog_id,
            payload=self._transaction_data,
            transaction_id=ledger_transaction.transaction_id
        )
        await self._transaction_repository.save(transaction)
        
        await self._drug_catalog_repository.status_update(
            self._catalog_id, status)

    async def execute(self):

        await self._ledger_service.insert_transaction(transaction_data)

        try:
            for mappings in self._mapping_parser.parse():
                await self._save_mappings(mappings)

            await self._ledger_service.insert_transaction(
                transaction_data.completed())

        except Exception as err:
            await self._ledger_service.insert_transaction(
                transaction_data.failed())

        await self._drug_repository.close_session()
