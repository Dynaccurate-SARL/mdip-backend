from fastapi import UploadFile
from datetime import datetime, timezone

from src.infrastructure.taskiq.broker import mapping_import_taskiq
from src.infrastructure.taskiq.mapping_import import MappingsTaskData
from src.utils.checksum import file_checksum
from src.domain.entities.drug_catalog import TaskStatus
from src.domain.entities.ltransactions import MappingTransaction, MappingTransactionData
from src.infrastructure.services.confidential_ledger.contract import LedgerInterface
from src.infrastructure.services.pandas_parser.mapping.parse import MappingParser
from src.infrastructure.repositories.contract import (
    MappingTransactionRepositoryInterface,
)


def _created_at():
    return datetime.now(timezone.utc).isoformat()


class MappingImportUseCase:
    def __init__(
        self,
        transaction_repository: MappingTransactionRepositoryInterface,
        ledger_service: LedgerInterface,
        mapping_parser: MappingParser,
        mapping_id: int,
        central_catalog_id: int,
        related_catalog_id: int,
    ):
        self._transaction_repository = transaction_repository
        self._ledger_service = ledger_service
        self._mapping_parser = mapping_parser
        self._mapping_id = mapping_id
        self._central_catalog_id = central_catalog_id
        self._related_catalog_id = related_catalog_id

    async def _update_status(self, status: TaskStatus):
        self._transaction_data["status"] = status
        self._transaction_data["created_at"] = _created_at()
        ledger_transaction = self._ledger_service.insert_transaction(
            self._transaction_data
        )

        transaction = MappingTransaction(
            transaction_id=ledger_transaction.transaction_id,
            mapping_id=self._mapping_id,
            catalog_id=self._central_catalog_id,
            related_catalog_id=self._related_catalog_id,
            payload=self._transaction_data,
        )
        await self._transaction_repository.save(transaction)

    async def prepare_task(self, file: UploadFile):
        self._transaction_data = MappingTransactionData(
            status="created",
            created_at=_created_at(),
            filename=file.filename,
            file_checksum=await file_checksum(file),
            created_at_tz="UTC",
            mapping_id=str(self._mapping_id),
            catalog_id=str(self._central_catalog_id),
            related_catalog_id=str(self._related_catalog_id),
        )
        await self._update_status("created")

    async def execute(self):
        await self._update_status("processing")

        for mappings in self._mapping_parser.parse():
            data = MappingsTaskData(
                mappings=mappings,
                central_catalog_id=self._central_catalog_id,
                related_catalog_id=self._related_catalog_id,
                mapping_id=self._mapping_id
            )
            await mapping_import_taskiq.kiq(data.model_dump())

        await self._update_status("completed")

        await self._transaction_repository.close_session()
