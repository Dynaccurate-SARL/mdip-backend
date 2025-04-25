from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import DrugCatalogRepositoryInterface, DrugRepositoryInterface
from src.infrastructure.services.confidential_ledger.contract import Ledger, TransactionData
from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from logging import getLogger


class CatalogImportUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface,
                 drug_repository: DrugRepositoryInterface,
                 catalog_id: int, parser: PandasParser, session: AsyncSession,
                 ledger_service: Ledger, logger: getLogger = None):
        self._drug_catalog_repository = drug_catalog_repository
        self._drug_repository = drug_repository
        self._catalog_id = catalog_id
        self._parser = parser
        self._session = session
        self._ledger_service = ledger_service
        self._logger = logger or getLogger(__name__)

    async def execute(self):
        transaction_data = TransactionData(
            entity_name=DrugCatalog.__tablename__,
            entity_id=self._catalog_id,
            status='processing',
            data={
                'type': 'catalog_import',
            }
        )

        self._logger.info(
            f"Catalog import process started for catalog_id={self._catalog_id}")
        await self._ledger_service.insert_transaction(transaction_data)
        await self._drug_catalog_repository.status_update(
            drug_catalog_id=self._catalog_id, status='processing')

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
            await self._drug_repository.delete_all_by_catalog_id(
                self._catalog_id)

            self._logger.error(
                f"Catalog import failed for catalog_id={self._catalog_id}")
            self._logger.exception(e)

        await self._drug_catalog_repository.status_update(
            drug_catalog_id=self._catalog_id, status=transaction_data.status)
        await self._ledger_service.insert_transaction(transaction_data)

        await self._drug_catalog_repository.close_session()
