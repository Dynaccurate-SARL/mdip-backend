import json
import sqlalchemy as sq
from typing import Dict
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeMeta

from src.infrastructure.db.base import Base


class LedgerTransaction(Base):
    __tablename__ = 'ledger_transactions'

    transaction_id: Mapped[str] = mapped_column(
        sq.String(50), primary_key=True, nullable=False)
    entity_name: Mapped[str] = mapped_column(sq.String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(sq.BigInteger, nullable=False)
    _content: Mapped[str] = mapped_column("content", sq.Text)

    created_at: Mapped[str] = mapped_column(
        sq.DateTime(timezone=True), server_default=sq.func.now())

    def __init__(self, transaction_id: str, entity_name: DeclarativeMeta,
                 entity_id: int, content: Dict = {}):
        self.entity_name = entity_name.__tablename__
        self.entity_id = entity_id
        self.transaction_id = transaction_id
        self._content = json.dumps(content)

    @property
    def content(self) -> Dict:
        return json.loads(self._content)

    @content.setter
    def content(self, value: Dict):
        self._content = json.dumps(value)
