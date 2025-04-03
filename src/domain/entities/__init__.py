from functools import lru_cache
from snowflake import SnowflakeGenerator
from sqlalchemy.orm import declarative_base


Base = declarative_base()


@lru_cache(maxsize=1)
def __get_snowflake_generator(instance: int = 1):
    return SnowflakeGenerator(instance)


def generate_snowflake_id() -> int:
    snowflake_gen = __get_snowflake_generator()
    return next(snowflake_gen)
