from datetime import datetime, timezone
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug_catalog import TaskStatus
from src.domain.entities.ltransactions import CatalogTransaction, CatalogTransactionData
from src.infrastructure.services.confidential_ledger.contract import LedgerInterface
from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.infrastructure.repositories.contract import (
    CatalogTransactionRepositoryInterface,
    DrugCatalogRepositoryInterface, DrugRepositoryInterface)
from src.utils.checksum import file_checksum


def _created_at():
    return datetime.now(timezone.utc).isoformat()


class CatalogImportUseCase:
    def __init__(
            self, drug_catalog_repository: DrugCatalogRepositoryInterface,
            transaction_repository: CatalogTransactionRepositoryInterface,
            drug_repository: DrugRepositoryInterface,
            ledger_service: LedgerInterface,
            catalog_id: int, parser: PandasParser, session: AsyncSession):
        self._drug_catalog_repository = drug_catalog_repository
        self._transaction_repository = transaction_repository
        self._drug_repository = drug_repository
        self._ledger_service = ledger_service
        self._catalog_id = catalog_id
        self._parser = parser
        self._session = session

    async def _update_status(self, status: TaskStatus):
        await self._drug_catalog_repository.status_update(
            self._catalog_id, status)
        self._transaction_data['status'] = status
        self._transaction_data['created_at'] = _created_at()
        ledger_transaction = self._ledger_service.insert_transaction(
            self._transaction_data)

        transaction = CatalogTransaction(
            transaction_id=ledger_transaction.transaction_id,
            catalog_id=self._catalog_id,
            payload=self._transaction_data
        )
        await self._transaction_repository.save(transaction)

    async def prepare_task(self, file: UploadFile):
        self._transaction_data = CatalogTransactionData(
            status='created',
            created_at=_created_at(),
            filename=file.filename,
            file_checksum=file_checksum(file),
            catalog_id=str(self._catalog_id),
            created_at_tz='UTC'
        )
        await self._update_status('created')

    async def execute(self):
        await self._update_status('processing')
        try:
            self._parser.parse()
            await self._parser.save_all(self._session, self._catalog_id)
            await self._update_status('completed')

        except Exception as e:
            await self._update_status('failed')
            await self._drug_repository.delete_all_by_catalog_id(
                self._catalog_id)
        finally:
            await self._drug_catalog_repository.close_session()
