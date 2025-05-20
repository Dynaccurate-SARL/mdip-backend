import sqlalchemy as sq

from src.domain.entities.ltransactions import MappingTransaction
from src.infrastructure.repositories.contract import MappingTransactionRepositoryInterface


class IMappingTransactionRepository(MappingTransactionRepositoryInterface):

    async def save(self, transaction: MappingTransaction):
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_id(self, id: int):
        result = await self.session.get(MappingTransaction, id)
        return result

    async def get_by_catalog_id(self, catalog_id: int):
        stmt = (
            sq.select(MappingTransaction)
            .where(MappingTransaction._catalog_id == catalog_id)
            .order_by(MappingTransaction._related_catalog_id.desc())
            .order_by(MappingTransaction._mapping_id.desc())
            .order_by(MappingTransaction._id.desc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()
