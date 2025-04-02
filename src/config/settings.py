import os
from typing import List, Literal
from functools import lru_cache
from pydantic_settings import BaseSettings


UploadStrategy = Literal['DISK', 'AZURE']
LedgerStrategy = Literal['DB', 'AZURE']


class Settings(BaseSettings):
    CORS_ORIGINS: List[str] = ['*']
    CORS_HEADERS: List[str] = ['*']
    CORS_METHODS: List[str] = ['*']

    JWT_SECRET: str = 'thisissecret'
    JWT_ACCESS_EXPIRATION: int = 900  # 900 seconds = 15 minutes
    JWT_REFRESH_EXPIRATION: int = 1800  # 1800 seconds = 30 minutes

    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    LEDGER_STRATEGY: Literal['DB', 'AZURE'] = 'DB'
    AZURE_LEDGER_URL: str = ''
    AZURE_CERTIFICATE_PATH: str = ''

    UPLOAD_STRATEGY: UploadStrategy = 'DISK'
    # strategy: disk
    DOCUMENTS_STORAGE_PATH: str = ''
    # strategy: azure
    AZURE_BLOB_CONTAINER_NAME: str = ''
    AZURE_BLOB_STORAGE_CONNECTION_STRING: str = ''


@lru_cache
def get_config() -> Settings:
    current_env = os.getenv('ENV', '').lower()
    if current_env == 'prod':
        return Settings()
    return Settings(_env_file='.env', _env_file_encoding='utf-8')
