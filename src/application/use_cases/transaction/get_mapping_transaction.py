from typing import List
from collections import defaultdict

from src.application.dto.transaction import MappingTransactionDto
from src.infrastructure.repositories.contract import (
    MappingTransactionRepositoryInterface,
)


class GetMappingTransactionUseCase:
    def __init__(self, mt_repository: MappingTransactionRepositoryInterface):
        self._mt_repository = mt_repository

    async def execute(self, catalog_id: int) -> List[List[MappingTransactionDto]]:
        transactions = await self._mt_repository.get_by_catalog_id(catalog_id)
        transactions_dtos = [
            MappingTransactionDto(
                transaction_id=transaction.transaction_id, **transaction.payload
            )
            for transaction in transactions
        ]

        grouped_transactions = defaultdict(list)
        for transaction in transactions_dtos:
            grouped_transactions[transaction.mapping_id].append(transaction)
        return list(grouped_transactions.values())
