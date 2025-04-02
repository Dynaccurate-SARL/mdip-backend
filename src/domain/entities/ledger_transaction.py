import json
import sqlalchemy as sq
from typing import TypedDict
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.domain.entities import Base, generate_snowflake_id


class LedgerTransactionContent(TypedDict):
    name: str
    filename: str
    file_checksum: str
    timestamp: datetime


class LedgerTransaction(Base):
    __tablename__ = 'ledger_transactions'

    id: Mapped[int] = mapped_column(
        sq.BigInteger, primary_key=True, nullable=False)
    transaction_id: Mapped[str] = mapped_column(sq.String(100), nullable=False)
    _content: Mapped[str] = mapped_column("content", nullable=False)

    def __init__(self, transaction_id: str, content: LedgerTransactionContent):
        self.id = generate_snowflake_id()
        self.transaction_id = transaction_id
        self._content = json.dumps(content)

    @property
    def content(self) -> LedgerTransactionContent:
        return json.loads(self._content)

    @content.setter
    def content(self, value: LedgerTransactionContent):
        self._content = json.dumps(value)
