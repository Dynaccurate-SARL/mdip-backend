import sqlalchemy as sq
from typing import Literal
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.infrastructure.db.base import IdMixin, Base
from src.application.dto.drug_catalog_dto import CountryCode

ImportStatus = Literal['created', 'processing', 'completed']


class DrugCatalog(IdMixin, Base):
    __tablename__ = 'drug_catalogs'

    name: Mapped[str] = mapped_column(sq.String(255), nullable=False)
    country: Mapped[CountryCode] = mapped_column(sq.String(2), nullable=False)
    version: Mapped[str] = mapped_column(sq.String(25), nullable=False)
    notes: Mapped[str] = mapped_column(sq.Text, nullable=True)
    status: Mapped[ImportStatus] = mapped_column(
        sq.String(10), nullable=False, default='created')

    def __init__(self, name: str, country: CountryCode,
                 version: str, notes: str):
        self.name = name
        self.country = country
        self.version = version
        self.notes = notes
