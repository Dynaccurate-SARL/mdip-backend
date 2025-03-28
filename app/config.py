import os
from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings


class UploadStrategy(Enum):
    DISK = 'DISK'
    AZURE = 'AZURE'

class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str
    LEDGER_TYPE: str = 'db'
    LEDGER_URL: str = ''
    CERTIFICATE_FILE: str = ''

    UPLOAD_STRATEGY: UploadStrategy = UploadStrategy.DISK
    # strategy: disk
    DOCUMENTS_STORAGE_PATH: str = ''
    # strategy: azure
    AZURE_BLOB_CONTAINER_NAME: str = ''
    AZURE_BLOB_STORAGE_CONNECTION_STRING: str = ''


@lru_cache
def get_config():
    current_env = os.getenv('ENV', '').lower()
    if current_env == 'prod':
        return Settings()
    return Settings(_env_file='.env', _env_file_encoding='utf-8')
