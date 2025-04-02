from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from abc import ABC, abstractmethod


class TransactionInserted(BaseModel):
    status: Literal['ready', 'processing']
    transaction_id: str
    content: dict


class TransactionData(BaseModel):
    name: str
    filename: str
    file_checksum: str
    timestamp: datetime


class Ledger(ABC):
    @abstractmethod
    async def insert_transaction(
            self, data: TransactionData) -> TransactionInserted:
        pass

    @abstractmethod
    async def retrieve_transaction(
            self, transaction_id: str) -> TransactionInserted | None:
        pass
