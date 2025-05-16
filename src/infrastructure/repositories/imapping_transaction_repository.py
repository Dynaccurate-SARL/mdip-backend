import sqlalchemy as sq

from src.domain.entities.ltransactions import MappingTransaction
from src.infrastructure.repositories.contract import MappingTransactionRepositoryInterface


class MappingTransactionRepository(MappingTransactionRepositoryInterface):

    async def save(self, transaction: MappingTransaction):
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_id(self, id: int):
        result = await self.session.get(MappingTransaction, id)
        return result

    async def get_latest_central_mappings(self, catalog_id: int):
        subquery = (
            sq.select(
                sq.func.max(MappingTransaction._id).label("max_id"),
            )
            .where(MappingTransaction._catalog_id == catalog_id)
            .group_by(
                MappingTransaction._catalog_id,
                MappingTransaction._related_catalog_id,
                MappingTransaction._mapping_id,
            )
            .subquery()
        )

        stmt = (
            sq.select(MappingTransaction)
            .join(
                subquery,
                MappingTransaction._id == subquery.c.max_id,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()
