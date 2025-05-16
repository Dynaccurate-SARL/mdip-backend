import uuid
import sqlalchemy as sq
from typing import Literal, TypedDict
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.drug_catalog import ImportStatus
from src.infrastructure.db.base import Base, IdMixin
from sqlalchemy.dialects.postgresql import UUID


class BaseTransactionData(TypedDict):
    status: ImportStatus
    filename: str
    file_checksum: str
    created_at: str
    created_at_tz: Literal['UTC']


class CatalogTransactionData(BaseTransactionData):
    catalog_id: str


class MappingTransactionData(BaseTransactionData):
    mapping_id: str
    from_catalog_id: str  # the catalog that the mapping is being created for
    to_catalog_id: str  # is always the central catalog


class BaseTransaction(IdMixin, Base):
    __abstract__ = True

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )


class CatalogTransaction(BaseTransaction):
    __tablename__ = 'catalog_transactions'

    _catalog_id: Mapped[int] = mapped_column(
        "catalog_id",
        sq.BigInteger, sq.ForeignKey('drug_catalogs.id'), nullable=False
    )
    payload: Mapped[CatalogTransactionData] = mapped_column(
        sq.JSON, nullable=False)
    
    def __init__(self, transaction_id: uuid.UUID, catalog_id: int, 
                 payload: CatalogTransactionData):
        self.transaction_id = transaction_id
        self.catalog_id = catalog_id
        self.payload = payload

    @property
    def catalog_id(self) -> str:
        return str(self._catalog_id)


class MappingTransaction(BaseTransaction):
    __tablename__ = 'mapping_transactions'

    _mapping_id: Mapped[int] = mapped_column(
        "mapping_id", sq.BigInteger, nullable=False
    )
    # is always the central catalog
    _catalog_id: Mapped[int] = mapped_column(
        "catalog_id", sq.BigInteger,
        sq.ForeignKey('drug_catalogs.id'), nullable=False
    )
    # the catalog that the mapping is being created for
    _related_catalog_id: Mapped[int] = mapped_column(
        "related_catalog_id", sq.BigInteger,
        sq.ForeignKey('drug_catalogs.id'), nullable=False
    )
    payload: Mapped[MappingTransactionData] = mapped_column(
        sq.JSON, nullable=False)

    @property
    def mapping_id(self) -> str:
        return str(self._mapping_id)

    @property
    def catalog_id(self) -> str:
        return str(self._catalog_id)

    @property
    def related_catalog_id(self) -> str:
        return str(self._related_catalog_id)
