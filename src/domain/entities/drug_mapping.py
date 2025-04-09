import sqlalchemy as sq
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.domain.entities import Base


class DrugMapping(Base):
    __tablename__ = 'drug_mappings'

    drug_id: Mapped[int] = mapped_column(
        sq.BigInteger, sq.ForeignKey('drugs.id'), nullable=False)
    related_drug_id: Mapped[int] = mapped_column(
        sq.BigInteger, sq.ForeignKey('drugs.id'), nullable=False)

    __table_args__ = (
        sq.PrimaryKeyConstraint('drug_id', 'related_drug_id',
                                name='uq_drug_related_drug'),
    )

    def __init__(self, drug_id: int, related_drug_id: int):
        self.drug_id = drug_id
        self.related_drug_id = related_drug_id
