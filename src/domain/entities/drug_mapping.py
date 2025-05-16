import sqlalchemy as sq
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.infrastructure.db.base import Base


class DrugMapping(Base):
    __tablename__ = 'drug_mappings'

    _mapping_id: Mapped[int] = mapped_column(
        'mapping_id', sq.BigInteger,
        sq.ForeignKey('mapping_transactions.mapping_id'), nullable=False)

    _drug_id: Mapped[int] = mapped_column(
        'drug_id', sq.BigInteger, sq.ForeignKey('drugs.id'),
        nullable=False)
    _related_drug_id: Mapped[int] = mapped_column(
        'related_drug_id', sq.BigInteger, sq.ForeignKey('drugs.id'),
        nullable=False)

    __table_args__ = (
        sq.PrimaryKeyConstraint('drug_id', 'related_drug_id',
                                name='uq_drug_related_drug'),
    )

    def __init__(self, mapping_id: int, drug_id: int, related_drug_id: int):
        self._mapping_id = mapping_id
        self._drug_id = drug_id
        self._related_drug_id = related_drug_id
