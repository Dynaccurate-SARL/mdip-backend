import json
import uuid
from src.domain.entities.ledger_transaction import LedgerTransaction
from src.infrastructure.repositories.contract import (
    LedgerTransactionRepositoryInterface)
from src.infrastructure.services.confidential_ledger.contract import (
    Ledger, TransactionData, TransactionInserted)


class DBLedgerService(Ledger):
    def __init__(self, lt_repository: LedgerTransactionRepositoryInterface):
        self.lt_repository = lt_repository

    async def insert_transaction(self, data: TransactionData):
        ltransaction = LedgerTransaction(
            transaction_id=str(uuid.uuid4()),
            entity_name=data.entity_name,
            entity_id=data.entity_id,
            content=data.model_dump(exclude_none=True, exclude={
                                    'entity_name', 'entity_id'}),
        )
        ltransaction = await self.lt_repository.save(ltransaction)

        return TransactionInserted(
            status='ready',
            content=ltransaction.content,
            transaction_id=ltransaction.transaction_id
        )

    async def retrieve_transaction(self, transaction_id: str):
        ltransaction = await self.lt_repository.get_by_transaction_id(
            transaction_id)
        if ltransaction:
            return TransactionInserted(
                status='ready',
                content=json.loads(ltransaction.content),
                transaction_id=ltransaction.transaction_id
            )
