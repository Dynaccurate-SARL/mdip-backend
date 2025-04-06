from datetime import datetime, timezone
from typing import Literal
from abc import ABC, abstractmethod
from sqlalchemy.orm import DeclarativeMeta

from src.application.dto import BaseSchema


class TransactionInserted(BaseSchema):
    status: Literal['ready', 'processing']
    transaction_id: str
    content: dict

class TransactionData(BaseSchema):
    # Entity transacton reference
    entity_name: DeclarativeMeta
    entity_id: int
    # Data that is sent to the ledger
    status: Literal['created', 'processing', 'completed']
    filename: str
    file_checksum: str
    catatag_hash: str
    created_at: str = datetime.now(timezone.utc).isoformat()
    created_at_tz: str = 'UTC'


class Ledger(ABC):
    @abstractmethod
    async def insert_transaction(
            self, data: TransactionData) -> TransactionInserted:
        pass

    @abstractmethod
    async def retrieve_transaction(
            self, transaction_id: str) -> TransactionInserted | None:
        pass
