from pydantic import EmailStr
from sqlalchemy import Sequence
from dataclasses import dataclass
from typing import Generic, List, TypeVar
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug import Drug
from src.domain.entities.user import User
from src.domain.entities.drug_catalog import DrugCatalog
from src.domain.entities.ledger_transaction import (
    LedgerTransaction)


T = TypeVar('T')


@dataclass
class PagedItems(Generic[T]):
    items: Sequence[T]
    total_count: int
    current_page: int
    page_size: int


class BaseRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session."""
        ...


class UserRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user to the database."""
        ...

    @abstractmethod
    async def get_by_sub(self, sub: str) -> User | None:
        """Get a user by their subject identifier."""
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
    async def get_by_id(self, entity_id: int) -> DrugCatalog | None:
        """Get a drug catalog by its ID."""
        ...

    @abstractmethod
    async def exists_central_catalog(self) -> bool:
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
        """Get a drug by their subject identifier."""
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
