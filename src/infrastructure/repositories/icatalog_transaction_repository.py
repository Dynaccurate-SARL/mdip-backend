import sqlalchemy as sq

from src.domain.entities.ltransactions import CatalogTransaction
from src.infrastructure.repositories.contract import CatalogTransactionRepositoryInterface


class ICatalogTransactionRepository(CatalogTransactionRepositoryInterface):

    async def save(self, transaction: CatalogTransaction):
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_id(self, id: int):
        result = await self.session.get(CatalogTransaction, id)
        return result

    async def get_latest_by_catalog_id(self, catalog_id: int):
        stmt = (
            sq.select(CatalogTransaction)
            .where(CatalogTransaction._catalog_id == catalog_id)
            .order_by(CatalogTransaction._id.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
