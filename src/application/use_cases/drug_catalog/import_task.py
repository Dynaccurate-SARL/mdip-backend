from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.services.confidential_ledger.contract import Ledger, TransactionData
from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class CatalogImportUseCase:
    def __init__(self, catalog_id: int, parser: PandasParser,
                 session: AsyncSession, ledger_service: Ledger):
        self._catalog_id = catalog_id
        self._parser = parser
        self._session = session
        self._ledger_service = ledger_service

    async def execute(self):
        transaction_data = TransactionData(
            entity_name=DrugCatalog,
            entity_id=self._catalog_id,
            status='processing'
        )
        await self._ledger_service.insert_transaction(transaction_data)
        try:
            self._parser.parse()
            await self._parser.save_all(session, catalog_id)
            transaction_data.status = 'completed'
        except Exception as e:
            transaction_data.status = 'failed'
        finally:
            await self._ledger_service.insert_transaction(transaction_data)
