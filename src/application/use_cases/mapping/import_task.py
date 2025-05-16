from datetime import datetime

from fastapi import UploadFile
from src.utils.checksum import file_checksum
from src.domain.entities.drug_catalog import TaskStatus
from src.domain.entities.drug_mapping import DrugMapping
from src.domain.entities.ltransactions import MappingTransaction, MappingTransactionData
from src.infrastructure.services.confidential_ledger.contract import LedgerInterface
from src.infrastructure.services.pandas_parser.mapping.parse import MappingParser
from src.infrastructure.repositories.contract import (
    DrugRepositoryInterface, MappingRepositoryInterface, 
    MappingTransactionRepositoryInterface)


def _created_at():
    return datetime.now(datetime.timezone.utc).isoformat()


class MappingImportUseCase:
    def __init__(
            self, drug_repository: DrugRepositoryInterface,
            transaction_repository: MappingTransactionRepositoryInterface,
            mapping_repository: MappingRepositoryInterface,
            ledger_service: LedgerInterface, mapping_parser: MappingParser,
            mapping_id: int, central_catalog_id: int, related_catalog_id: int):
        self._drug_repository = drug_repository
        self._transaction_repository = transaction_repository
        self._mapping_repository = mapping_repository
        self._ledger_service = ledger_service
        self._mapping_parser = mapping_parser
        self._mapping_id = mapping_id
        self._central_catalog_id = central_catalog_id
        self._related_catalog_id = related_catalog_id

    async def _save_mappings(self, mappings: list[DrugMapping]):
        for mapping in mappings:
            central_catalog_drug = await self._drug_repository.\
                get_by_drug_code_on_catalog_id(
                    self._central_catalog_id, mapping.drug_code)
            if central_catalog_drug:
                related_catalog_drug = await self._drug_repository.\
                    get_by_drug_code_on_catalog_id(
                        self._related_catalog_id, mapping.related_drug_code)
                try:
                    mapping = DrugMapping(
                        mapping_id=self._mapping_id,
                        drug_id=central_catalog_drug._id,
                        related_drug_id=related_catalog_drug._id)
                    await self._mapping_repository.save(mapping)
                except Exception:
                    pass

    async def _update_status(self, status: TaskStatus):
        self._transaction_data['status'] = status
        self._transaction_data['created_at'] = _created_at()
        ledger_transaction = self._ledger_service.insert_transaction(
            self._transaction_data)

        transaction = MappingTransaction(
            transaction_id=ledger_transaction.transaction_id,
            mapping_id=self._mapping_id,
            catalog_id=self._central_catalog_id,
            related_catalog_id=self._related_catalog_id,
            payload=self._transaction_data
        )
        await self._transaction_repository.save(transaction)

        await self._drug_catalog_repository.status_update(
            self._catalog_id, status)

    async def prepare_task(self, file: UploadFile):
        self._transaction_data = MappingTransactionData(
            status='created',
            created_at=_created_at(),
            filename=file.filename,
            file_checksum=file_checksum(file),
            created_at_tz='UTC',
            mapping_id=str(self._mapping_id),
            catalog_id=str(self._central_catalog_id),
            related_catalog_id=str(self._related_catalog_id)
        )
        await self._update_status('created')

    async def execute(self):
        await self._update_status('processing')

        try:
            for mappings in self._mapping_parser.parse():
                await self._save_mappings(mappings)
            await self._update_status('completed')
        except Exception as err:
            await self._update_status('failed')
            await self._mapping_repository.delete_all_by_mapping_id(
                self._mapping_id)

        await self._drug_repository.close_session()
