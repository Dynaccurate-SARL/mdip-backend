from datetime import datetime, timezone
import os
from typing import Literal
from abc import ABC, abstractmethod

from src.application.dto import BaseSchema


class TransactionInserted(BaseSchema):
    status: Literal['ready', 'processing']
    transaction_id: str | None = None
    content: dict | None = None


def _created_at() -> str:
    if os.getenv('ENV', None) == 'TEST':
        date = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        return date.isoformat()
    return datetime.now(timezone.utc).isoformat()


class TransactionData(BaseSchema):
    # Entity transacton reference
    entity_name: str
    entity_id: int
    # Data that is sent to the ledger
    status: Literal['created', 'processing', 'completed', 'failed']
    data: dict | None = None
    created_at: str = _created_at()
    created_at_tz: str = 'UTC'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TransactionData):
            return False
        def object_to_dict(instance: TransactionData) -> dict:
            return {
                'entity_name': instance.entity_name,
                'entity_id': instance.entity_id,
                'status': instance.status,
                'data': instance.data
            }
        return object_to_dict(self) == object_to_dict(other)

    def completed(self) -> 'TransactionData':
        return TransactionData(
            entity_name=self.entity_name,
            entity_id=self.entity_id,
            status='completed',
            data=self.data,
            created_at=self.created_at,
            created_at_tz=self.created_at_tz
        )

    def failed(self) -> 'TransactionData':
        return TransactionData(
            entity_name=self.entity_name,
            entity_id=self.entity_id,
            status='failed',
            data=self.data,
            created_at=self.created_at,
            created_at_tz=self.created_at_tz
        )


class Ledger(ABC):
    @abstractmethod
    async def insert_transaction(
            self, data: TransactionData) -> TransactionInserted:
        pass

    @abstractmethod
    async def retrieve_transaction(
            self, transaction_id: str) -> TransactionInserted | None:
        pass
