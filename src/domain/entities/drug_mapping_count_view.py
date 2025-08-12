import sqlalchemy as sq
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.infrastructure.db.base import Base


class DrugMappingCountView(Base):
    __tablename__ = "drug_mappings_stats"
    __table_args__ = {"info": {"is_view": True}}

    drug_id: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True)
    drug_name: Mapped[str] = mapped_column(sq.String)
    drug_code: Mapped[str] = mapped_column(sq.String)
    mapping_count: Mapped[int] = mapped_column(sq.Integer)
