import sqlalchemy as sq
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.infrastructure.db.base import IdMixin, Base
from src.application.dto.drug_catalog_dto import CountryCode, TaskStatus


class DrugCatalog(IdMixin, Base):
    __tablename__ = "drug_catalogs"

    name: Mapped[str] = mapped_column(sq.String(255), nullable=False)
    country: Mapped[CountryCode] = mapped_column(sq.String(2), nullable=False)
    version: Mapped[str] = mapped_column(sq.String(25), nullable=False)
    notes: Mapped[str] = mapped_column(sq.Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        sq.String(10), nullable=False, default="created"
    )
    is_central: Mapped[bool] = mapped_column(sq.Boolean, nullable=False, default=False)

    def __init__(
        self,
        name: str,
        country: CountryCode,
        version: str,
        notes: str,
        is_central: bool = False,
    ):
        self.name = name
        self.country = country
        self.version = version
        self.is_central = is_central
        self.notes = notes

    @staticmethod
    def _mock(number: int = 1, status: TaskStatus = "created") -> "DrugCatalog":
        catalog = DrugCatalog(
            name=f"Drug Catalog {number}",
            country="CA",
            version=f"{number}.0",
            is_central=False,
            notes=f"Note {number}",
        )
        catalog._id = number
        catalog.status = status
        return catalog
