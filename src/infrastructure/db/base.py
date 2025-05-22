from typing import Any
import sqlalchemy as sq
from functools import lru_cache
from pydantic_core import core_schema
from snowflake import SnowflakeGenerator
from sqlalchemy.orm import Mapped, mapped_column, declarative_base


Base = declarative_base()


@lru_cache(maxsize=1)
def __get_snowflake_generator(instance: int = 1):
    return SnowflakeGenerator(instance)


def generate_snowflake_id() -> int:
    snowflake_gen = __get_snowflake_generator()
    return next(snowflake_gen)


class IdMixin:
    _id: Mapped[int] = mapped_column(
        "id",
        sq.BigInteger,
        primary_key=True,
        nullable=False,
        default=generate_snowflake_id,
    )

    @property
    def id(self) -> str:
        return str(self._id)


class IdInt(str):
    @classmethod
    def validate(cls, value: Any) -> int:
        def is_64bits(num):
            return -(2**63) <= num < 2**63

        if not (isinstance(value, str) and value.isdigit()):
            raise ValueError("Value must be a string representing an integer")
        int_value = int(value)
        if not is_64bits(int_value):
            raise ValueError("Value must be a 64-bit integer")
        return int_value

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any):
        return core_schema.no_info_after_validator_function(
            cls.validate, core_schema.str_schema()
        )
