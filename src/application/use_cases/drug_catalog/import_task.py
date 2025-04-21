from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.services.confidential_ledger.contract import Ledger, TransactionData
from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from logging import getLogger


class CatalogImportUseCase:
    def __init__(self, catalog_id: int, parser: PandasParser,
                 session: AsyncSession, ledger_service: Ledger,
                 logger: getLogger = None):
        self._logger = logger or getLogger(__name__)
        self._catalog_id = catalog_id
        self._parser = parser
        self._session = session
        self._ledger_service = ledger_service

    async def execute(self):
        self._logger.info(
            "Starting catalog import for catalog_id=%s", self._catalog_id)

        transaction_data = TransactionData(
            entity_name=DrugCatalog,
            entity_id=self._catalog_id,
            status='processing'
        )
        self._logger.info(
            f"Catalog import process started for catalog_id={self._catalog_id}")
        await self._ledger_service.insert_transaction(transaction_data)

        try:
            self._logger.info(
                f"Parsing data for catalog_id={self._catalog_id}")
            
            self._parser.parse()
            await self._parser.save_all(self._session, self._catalog_id)
            transaction_data.status = 'completed'
            
            self._logger.info(
                f"Catalog import completed successfully for catalog_id={self._catalog_id}")
        except Exception as e:
            transaction_data.status = 'failed'
            self._logger.error(
                f"Catalog import failed for catalog_id={self._catalog_id}")
            self._logger.exception(e)

        return await self._ledger_service.insert_transaction(transaction_data)
