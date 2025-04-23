from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ledger_transaction import LedgerTransaction
from src.infrastructure.repositories.contract import LedgerTransactionRepositoryInterface


class ILedgerTransactionRepository(LedgerTransactionRepositoryInterface):

    async def save(self, transaction: LedgerTransaction):
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_transaction_id(self, transaction_id: int):
        stmt = select(LedgerTransaction).where(
            LedgerTransaction.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
