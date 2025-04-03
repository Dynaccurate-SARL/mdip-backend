import os
import logging as log
from typing import Union, Iterable, AnyStr, IO

FileData = Union[bytes, str, Iterable[AnyStr], IO[AnyStr]]


class DiskFileService:
    def __init__(self, storage_path: str):
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        self.storage_path = storage_path

    def upload_file(self, name: str, file_data: FileData) -> str:
        """Returns the path of the uploaded file."""
        file_path = os.path.join(self.storage_path, name)
        with open(file_path, "wb") as f:
            f.write(file_data)
        log.info(f"File uploaded to disk: {file_path}")
        return file_path

    def download_file(self, name: str) -> str:
        """Returns the path of the downloaded file."""
        file_path = os.path.join(self.storage_path, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError
        return file_path

    def delete_file(self, name: str):
        try:
            file_path = os.path.join(self.storage_path, name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            log.error(f"Error deleting file from disk: {name}. Error: {e}")
