from os import getenv
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings

from src.config.settings.base import BaseEnvs
from src.config.settings.blob import BlobEnvs
from src.config.settings.ledger import LedgerEnvs


class Envs(LedgerEnvs, BlobEnvs, BaseEnvs, BaseSettings): ...


@lru_cache
def get_config(env: Literal["TEST"] | None = getenv("ENVIRONMENT", None)) -> Envs:
    if env == "TEST":
        return Envs(
            RABBITMQ_URL="amqp://guest:guest@localhost:5672/fake_vhost",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            UPLOAD_STRATEGY="DISK",
            _env_file=".env.test",
            _env_file_encoding="utf-8",
        )
    return Envs(_env_file=".env", _env_file_encoding="utf-8")
