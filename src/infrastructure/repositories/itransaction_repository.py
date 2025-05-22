from uuid import UUID
from sqlalchemy import bindparam, select, union_all

from src.infrastructure.repositories.contract import TransactionRepositoryInterface
from src.domain.entities.ltransactions import (
    CatalogTransaction,
    CatalogTransactionData,
    MappingTransaction,
    MappingTransactionData,
)


class ITransactionRepository(TransactionRepositoryInterface):
    async def get_payload_by_transaction_id(
        self, transaction_id: UUID
    ) -> MappingTransactionData | CatalogTransactionData:
        stmt1 = select(CatalogTransaction.payload).where(
            CatalogTransaction.transaction_id == bindparam("tid1")
        )
        stmt2 = select(MappingTransaction.payload).where(
            MappingTransaction.transaction_id == bindparam("tid2")
        )

        stmt = union_all(stmt1, stmt2)
        result = await self.session.execute(
            stmt, {"tid1": transaction_id, "tid2": transaction_id}
        )
        return result.scalar_one_or_none()
