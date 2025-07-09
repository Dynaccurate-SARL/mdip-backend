from typing import Dict, Literal
from typing_extensions import TypedDict
from abc import ABC, abstractmethod

from src.application.dto import BaseSchema


class TransactionData(TypedDict):
    data: Dict[str, str]
    hash: str


class TransactionInserted(BaseSchema):
    transaction_id: str
    status: Literal["ready", "processing"]
    transaction_data: TransactionData | None = None


class LedgerInterface(ABC):
    @abstractmethod
    def insert_transaction(self, data: dict) -> TransactionInserted:
        pass

    @abstractmethod
    def retrieve_transaction(self, transaction_id: str) -> TransactionInserted | None:
        pass
