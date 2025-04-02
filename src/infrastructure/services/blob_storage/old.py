import os
import tempfile
import logging as log
from src.config.settings import get_config, UploadStrategy
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient
from typing import Union, Iterable, AnyStr, IO

FileData = Union[bytes, str, Iterable[AnyStr], IO[AnyStr]]


class AzureFileService:
    def __init__(self):
        self.container_client = self.__get_azure_container_client()

    def __get_azure_container_client(self) -> ContainerClient:
        blob_service_client = BlobServiceClient.from_connection_string(
            get_config().AZURE_BLOB_STORAGE_CONNECTION_STRING)
        return blob_service_client.get_container_client(get_config().AZURE_BLOB_CONTAINER_NAME)

    def upload_file(self, name: str, file_data: FileData) -> str:
        self.container_client.upload_blob(name, data=file_data, overwrite=True)
        log.info(f"File uploaded to azure: {name}")
        return name

    def download_file(self, name: str) -> str:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, name)
        with open(file_path, mode="wb") as download_file:
            download_file.write(
                self.container_client.download_blob(name).readall())
        return file_path

    def delete_file(self, name: str):
        try:
            self.container_client.delete_blob(name)
        except Exception as e:
            log.error(f"Error deleting file from Azure: {name}. Error: {e}")


class DiskFileService:
    def __init__(self):
        self.storage_path = get_config().DOCUMENTS_STORAGE_PATH
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def upload_file(self, name: str, file_data: FileData) -> str:
        destination_file_path = os.path.join(self.storage_path, name)
        with open(destination_file_path, "wb") as f:
            f.write(file_data)
        log.info(f"File uploaded to disk: {destination_file_path}")
        return destination_file_path

    def download_file(self, name: str) -> str:
        destination_file_path = os.path.join(self.storage_path, name)
        if not os.path.exists(destination_file_path):
            raise FileNotFoundError
        return destination_file_path

    def delete_file(self, name: str):
        try:
            file_path = os.path.join(self.storage_path, name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            log.error(f"Error deleting file from disk: {name}. Error: {e}")


class FileService:
    def __init__(self):
        if get_config().UPLOAD_STRATEGY == UploadStrategy.AZURE:
            self.service = AzureFileService()
        else:
            self.service = DiskFileService()

    def upload_file(self, name: str, file_data: FileData) -> str:
        return self.service.upload_file(name, file_data)

    def download_file(self, name: str) -> str:
        return self.service.download_file(name)

    def delete_file(self, name: str):
        self.service.delete_file(name)
