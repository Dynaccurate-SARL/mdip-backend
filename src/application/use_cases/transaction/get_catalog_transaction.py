from typing import List

from src.application.dto.transaction import CatalogTransactionDto
from src.infrastructure.repositories.contract import (
    CatalogTransactionRepositoryInterface,
)


class GetCatalogTransactionsUseCase:
    def __init__(self, ct_repository: CatalogTransactionRepositoryInterface):
        self._ct_repository = ct_repository

    async def execute(self, catalog_id: int) -> List[CatalogTransactionDto]:
        transactions = await self._ct_repository.get_all_by_catalog_id(catalog_id)
        return [
            CatalogTransactionDto(
                transaction_id=transaction.transaction_id, **transaction.payload
            )
            for transaction in transactions
        ]
