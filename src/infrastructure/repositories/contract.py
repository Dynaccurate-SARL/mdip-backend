from pydantic import EmailStr
from sqlalchemy import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

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
        ...


class UserRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, user: User) -> User:
        ...

    @abstractmethod
    async def get_user_by_sub(self, sub: str) -> User | None:
        ...

    @abstractmethod
    async def get_user_by_email(self, email: EmailStr) -> User | None:
        ...


class DrugCatalogRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, entity: DrugCatalog) -> DrugCatalog:
        ...

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> DrugCatalog | None:
        ...

    @abstractmethod
    async def get_total_count(self, name_filter: str = None) -> int:
        ...

    @abstractmethod
    async def get_paginated(
            self, page: int, page_size: int,
            name_filter: str = None) -> PagedItems[DrugCatalog]:
        ...


class LedgerTransactionRepositoryInterface(BaseRepository):
    @abstractmethod
    async def save(self, transaction: LedgerTransaction) -> LedgerTransaction:
        ...

    @abstractmethod
    async def get_by_transaction_id(
            self, transaction_id: int) -> LedgerTransaction | None:
        ...
