from fastapi import UploadFile

from src.config.settings import Envs, get_config
from src.infrastructure.services.blob_storage.azure_storage import AzureFileService
from src.infrastructure.services.blob_storage.disk_storage import DiskFileService


async def upload_file(
        filename: str, source: UploadFile, config: Envs = get_config()) -> str:
    """Uploads a file to the designated storage."""
    if config.UPLOAD_STRATEGY == "AZURE":
        service = AzureFileService(
            config.AZURE_BLOB_CONTAINER_NAME,
            config.AZURE_BLOB_STORAGE_CONNECTION_STRING,
        )
    else:
        service = DiskFileService(
            config.DOCUMENTS_STORAGE_PATH)
    return await service.upload_file(filename, source)


async def get_file(filename: str, config: Envs = get_config()) -> str:
    """Returns the path to the downloaded file."""
    if config.UPLOAD_STRATEGY == "AZURE":
        service = AzureFileService(
            config.AZURE_BLOB_CONTAINER_NAME,
            config.AZURE_BLOB_STORAGE_CONNECTION_STRING,
        )
    else:
        service = DiskFileService(config.DOCUMENTS_STORAGE_PATH)
    return await service.get_file(filename)
