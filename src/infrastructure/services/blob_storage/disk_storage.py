import os

from fastapi import UploadFile
import aiofiles

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB


class DiskFileService:
    def __init__(self, storage_path: str):
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        self.storage_path = storage_path

    async def upload_file(self, filename: str, source: UploadFile):
        """Returns the path of the uploaded file."""
        dest_path = os.path.join(self.storage_path, filename)
        async with aiofiles.open(dest_path, "wb") as out_file:
            while True:
                chunk = await source.read(CHUNK_SIZE)
                if not chunk:
                    break
                await out_file.write(chunk)
            return dest_path

    async def get_file(self, filename: str) -> str:
        """Returns the path of the downloaded file."""
        file_path = os.path.join(self.storage_path, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Blob '{filename}' not found in the container.")
        return file_path
