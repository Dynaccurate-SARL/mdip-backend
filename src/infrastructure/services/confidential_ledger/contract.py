from uuid import UUID
from typing import Dict, Literal
from abc import ABC, abstractmethod

from src.application.dto import BaseSchema


class TransactionInserted(BaseSchema):
    transaction_id: UUID
    status: Literal['ready', 'processing']
    transaction_data: Dict | None = None


class LedgerInterface(ABC):
    @abstractmethod
    def insert_transaction(self, data: dict) -> TransactionInserted:
        pass

    @abstractmethod
    def retrieve_transaction(
            self, transaction_id: UUID) -> TransactionInserted | None:
        pass
