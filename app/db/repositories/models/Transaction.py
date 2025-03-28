from datetime import datetime

from sqlalchemy import func
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ...base import BaseMixin, Base


class Transaction(Base, BaseMixin):
    __tablename__ = 'transaction'

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    _entity_id: Mapped[int] = mapped_column(ForeignKey('entity.id'))
    content: Mapped[str] = mapped_column(nullable=True)

    @property
    def entity_id(self) -> int:
        return self._entity_id