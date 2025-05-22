from uuid import UUID

from src.utils.checksum import dict_hash
from src.application.dto.transaction import TransactionDto
from src.infrastructure.repositories.contract import TransactionRepositoryInterface
from src.infrastructure.services.confidential_ledger.contract import LedgerInterface


class VerifyTransactionUseCase:
    def __init__(
        self,
        t_repository: TransactionRepositoryInterface,
        ledger_service: LedgerInterface,
    ):
        self._t_repository = t_repository
        self._ledger_service = ledger_service

    async def execute(self, transaction_id: UUID) -> TransactionDto:
        payload = await self._t_repository.get_payload_by_transaction_id(transaction_id)
        if payload is None:
            return TransactionDto(valid=False)

        transaction = self._ledger_service.retrieve_transaction(transaction_id)
        if transaction is None:
            return TransactionDto(valid=False)

        valid = dict_hash(payload) == transaction.transaction_data["hash"]
        return TransactionDto(valid=valid)
