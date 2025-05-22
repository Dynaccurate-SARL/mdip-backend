import os
import tempfile
import logging as log
from azure.storage.blob import BlobServiceClient
from typing import Union, Iterable, AnyStr, IO

FileData = Union[bytes, str, Iterable[AnyStr], IO[AnyStr]]


class AzureFileService:
    def __init__(self, container_name: str, storage_connection_string: str):
        blob_service_client = BlobServiceClient.from_connection_string(
            storage_connection_string
        )
        self._container_client = blob_service_client.get_container_client(
            container_name
        )

    def upload_file(self, name: str, file_data: FileData):
        self._container_client.upload_blob(name, data=file_data, overwrite=True)
        log.info(f"File uploaded to azure: {name}")

    def download_file(self, name: str) -> str:
        """Returns the path to the downloaded file."""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, name)
        with open(file_path, mode="wb") as download_file:
            download_file.write(self._container_client.download_blob(name).readall())
        return file_path

    def delete_file(self, name: str):
        try:
            self._container_client.delete_blob(name)
        except Exception as e:
            log.error(f"Error deleting file from Azure: {name}. Error: {e}")
