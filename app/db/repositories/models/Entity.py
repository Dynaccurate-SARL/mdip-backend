import enum
from typing import List
from datetime import datetime
from sqlalchemy import Enum

from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column

from ...base import BaseMixin, Base
from .Transaction import Transaction


class EntityStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    DONE = 'done'


class Entity(Base, BaseMixin):
    __tablename__ = 'entity'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement='auto')

    entity_type: Mapped[str]
    origin: Mapped[str]
    destination: Mapped[str]
    size: Mapped[float]
    unit: Mapped[str]
    status: Mapped[EntityStatus] = mapped_column(Enum(
        EntityStatus, create_constraint=True, validate_strings=True), default=EntityStatus.PENDING)
    reg_transactions: Mapped[List["Transaction"]] = relationship()

    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        onupdate=func.now(), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
