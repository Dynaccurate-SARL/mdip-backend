import sqlalchemy as sq
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.domain.entities import Base, IdMixin


class Drug(IdMixin, Base):
    __tablename__ = 'drugs'

    catalog_id: Mapped[int] = mapped_column(
        sq.BigInteger, sq.ForeignKey('drug_catalogs.id'), nullable=False)
    drug_code: Mapped[str] = mapped_column(sq.String, nullable=False)
    drug_name: Mapped[str] = mapped_column(sq.String, nullable=False)
    properties: Mapped[dict] = mapped_column(sq.JSON, nullable=True)

    def __init__(self, catalog_id: int, drug_code: str,
                 drug_name: str, properties: dict):
        self.catalog_id = catalog_id
        self.drug_code = drug_code
        self.drug_name = drug_name
        self.properties = properties
