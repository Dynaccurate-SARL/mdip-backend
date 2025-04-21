import sqlalchemy as sq
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.infrastructure.db.base import Base, IdMixin


class Drug(IdMixin, Base):
    __tablename__ = 'drugs'

    _catalog_id: Mapped[int] = mapped_column(
        "catalog_id", sq.BigInteger, sq.ForeignKey('drug_catalogs.id'),
        nullable=False)
    drug_code: Mapped[str] = mapped_column(sq.String, nullable=False)
    drug_name: Mapped[str] = mapped_column(sq.String, nullable=False)
    properties: Mapped[dict] = mapped_column(sq.JSON, nullable=True)

    @property
    def catalog_id(self) -> str:
        return str(self._catalog_id)

    def __init__(self, catalog_id: int, drug_code: str,
                 drug_name: str, properties: dict):
        self._catalog_id = catalog_id
        self.drug_code = drug_code
        self.drug_name = drug_name
        self.properties = properties

    @staticmethod
    def _mock(number: int = 1) -> 'Drug':
        drug = Drug(
            catalog_id=number,
            drug_code=f"A{number}",
            drug_name=f"Drug {number}",
            properties={"key": "value"}
        )
        drug._id = number
        return drug
