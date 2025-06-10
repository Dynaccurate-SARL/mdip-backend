import asyncio
import logging
import traceback
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug_catalog import TaskStatus
from src.domain.entities.ltransactions import CatalogTransaction, CatalogTransactionData
from src.infrastructure.services.confidential_ledger.contract import LedgerInterface
from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.infrastructure.repositories.contract import (
    CatalogTransactionRepositoryInterface,
    DrugCatalogRepositoryInterface,
    DrugRepositoryInterface,
)
from src.utils.checksum import file_checksum


def _created_at():
    return datetime.now(timezone.utc).isoformat()


class CatalogImportUseCase:
    def __init__(
        self,
        drug_catalog_repository: DrugCatalogRepositoryInterface,
        transaction_repository: CatalogTransactionRepositoryInterface,
        drug_repository: DrugRepositoryInterface,
        ledger_service: LedgerInterface,
        catalog_id: int,
        parser: PandasParser,
        session: AsyncSession,
    ):
        self._drug_catalog_repository = drug_catalog_repository
        self._transaction_repository = transaction_repository
        self._drug_repository = drug_repository
        self._ledger_service = ledger_service
        self._catalog_id = catalog_id
        self._parser = parser
        self._session = session
        self._logger = logging.getLogger(__name__)

    async def _update_status(self, status: TaskStatus):
        self._logger.info(
            f"Updating catalog {self._catalog_id} status to '{status}'")
        await self._drug_catalog_repository.status_update(self._catalog_id, status)
        self._transaction_data["status"] = status
        self._transaction_data["created_at"] = _created_at()
        self._logger.info("Inserting transaction into ledger")
        ledger_transaction = self._ledger_service.insert_transaction(
            self._transaction_data
        )

        transaction = CatalogTransaction(
            transaction_id=ledger_transaction.transaction_id,
            catalog_id=self._catalog_id,
            payload=self._transaction_data,
        )
        self._logger.info("Saving transaction in repository")
        await self._transaction_repository.save(transaction)

    async def prepare_transaction_data(self, filename: str, source: str):
        self._logger.info(
            f"Preparing task for file '{filename}' of catalog {self._catalog_id}")
        self._transaction_data = CatalogTransactionData(
            status="created",
            created_at=_created_at(),
            filename=filename,
            file_checksum=await file_checksum(source),
            catalog_id=str(self._catalog_id),
            created_at_tz="UTC",
        )
        await self._update_status("created")
        await asyncio.sleep(2)

    async def execute(self):
        self._logger.info(f"Starting execution of catalog {self._catalog_id}")
        await self._update_status("processing")
        await asyncio.sleep(5)

        try:
            self._logger.info("Starting file parsing")
            self._parser.parse()

            self._logger.info("Saving parsed data to database")
            await self._parser.save_all(self._session, self._catalog_id)

            self._logger.info("Updating status to 'completed'")
            await self._update_status("completed")

        except Exception as err:
            logger = logging.getLogger("uvicorn.error")
            logger.error(f"Catalog ID: {self._catalog_id}")
            logger.error("Error during catalog import: %s\n%s",
                         err, traceback.format_exc())

            self._logger.info("Updating status to 'failed' due to error")
            await self._update_status("failed")
            self._logger.info(
                "Removing all drug records from catalog due to failure")
            await self._drug_repository.delete_all_by_catalog_id(self._catalog_id)
