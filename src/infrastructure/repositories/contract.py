from pydantic import EmailStr
from sqlalchemy import Sequence
from dataclasses import dataclass
from typing import Generic, List, TypeVar
from abc import abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.drug_catalog_dto import CountryCode
from src.domain.entities.drug import Drug
from src.domain.entities.user import User
from src.domain.entities.drug_mapping import DrugMapping
from src.domain.entities.drug_catalog import DrugCatalog, ImportStatus
from src.domain.entities.ledger_transaction import (
    LedgerTransaction)


T = TypeVar('T')


@dataclass
class PagedItems(Generic[T]):
    items: Sequence[T]
    total_count: int
    current_page: int
    page_size: int


class BaseRepository():
    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session."""
        self.session = session

    async def close_session(self):
        """Close the database session."""
        try:
            await self.session.close()
        except Exception:
            ...


class UserRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user to the database."""
        ...

    @abstractmethod
    async def get_by_sub(self, sub: int) -> User | None:
        """Get a user by their id."""
        ...

    @abstractmethod
    async def get_user_by_email(self, email: EmailStr) -> User | None:
        """Get a user by their email address."""
        ...


class DrugCatalogRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, entity: DrugCatalog) -> DrugCatalog:
        """Save a drug catalog to the database."""
        ...

    @abstractmethod
    async def get_by_id(self, drug_catalog_id: int) -> DrugCatalog | None:
        """Get a drug catalog by its ID."""
        ...

    @abstractmethod
    async def status_update(self, drug_catalog_id: int, status: ImportStatus):
        """Update the import status of a drug catalog."""
        ...

    @abstractmethod
    async def get_central(self) -> DrugCatalog | None:
        """Check if a central drug catalog exists."""
        ...

    @abstractmethod
    async def get_total_count(self, name_filter: str = None) -> int:
        """Get the total count of drug catalogs, optionally filtered by name."""
        ...

    @abstractmethod
    async def get_paginated(
            self, page: int, page_size: int,
            name_filter: str = None) -> PagedItems[DrugCatalog]:
        """Get paginated drug catalogs, optionally filtered by name."""
        ...


class LedgerTransactionRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, transaction: LedgerTransaction) -> LedgerTransaction:
        """Save a ledger transaction to the database."""
        ...

    @abstractmethod
    async def get_by_transaction_id(
            self, transaction_id: int) -> LedgerTransaction | None:
        """Get a ledger transaction by its ID."""
        ...


class DrugRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, drug: Drug) -> Drug:
        """Save a drug to the database."""
        ...

    @abstractmethod
    async def get_by_id(self, id: int) -> Drug | None:
        """Get a drug by its ID."""

    @abstractmethod
    async def delete_all_by_catalog_id(self, catalog_id: int):
        """Delete all drugs associated with a specific catalog ID."""
        ...

    @abstractmethod
    async def get_by_drug_code_on_catalog_id(
            self, catalog_id: int, drug_code: str) -> Drug | None:
        """Get a drug by its drug code."""
        ...

    @abstractmethod
    async def get_all_like_code_or_name(self, name_or_code: str) -> List[Drug]:
        """Get all drugs that match the given name or code."""
        ...

    @abstractmethod
    async def get_total_count(self, drug_catalog_id: int,
                              name_or_code_filter: str = None) -> int:
        """Get the total count of drugs, optionally filtered by name or code."""
        ...

    @abstractmethod
    async def get_paginated_by_catalog_id(
            self, page: int, page_size: int, drug_catalog_id: int,
            name_or_code_filter: str = None) -> PagedItems[Drug]:
        """Get paginated drugs, optionally filtered by name or code."""
        ...


@dataclass
class CentralDrugMapping:
    id: int
    drug_name: str
    drug_code: str
    country: CountryCode
    properties: dict


class MappingRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, mapping: DrugMapping) -> DrugMapping:
        """Save a drug to the database."""
        ...

    @abstractmethod
    async def get_mappings_by_central_drug_id(
            self, central_drug_id: int) -> List[CentralDrugMapping]:
        """Get all mappings for a given central drug ID."""
        ...
