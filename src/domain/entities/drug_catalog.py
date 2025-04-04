import sqlalchemy as sq
from typing import Literal
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.domain.entities import Base, generate_snowflake_id
from src.application.dto.drug_catalog_dto import CountryCode


class DrugCatalog(Base):
    __tablename__ = 'drug_catalogs'

    id: Mapped[int] = mapped_column(
        sq.BigInteger, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(sq.String(255), nullable=False)
    country: Mapped[CountryCode] = mapped_column(sq.String(2), nullable=False)
    version: Mapped[str] = mapped_column(sq.String(25), nullable=False)
    notes: Mapped[str] = mapped_column(sq.Text, nullable=True)

    def __init__(self, name: str, country: CountryCode, 
                 version: str, notes: str):
        self.id = generate_snowflake_id()
        self.name = name
        self.country = country
        self.version = version
        self.notes = notes