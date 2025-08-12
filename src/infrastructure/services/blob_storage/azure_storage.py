import os
import tempfile
import aiofiles
import logging as log
from azure.storage.blob.aio import BlobServiceClient

from fastapi import UploadFile

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB


class AzureFileService:
    def __init__(self, container_name: str, storage_connection_string: str):
        self._storage_connection_string = storage_connection_string
        self._container_name = container_name

    async def upload_file(self, filename: str, source: UploadFile):
        blob_service_client = BlobServiceClient.from_connection_string(
            self._storage_connection_string
        )
        async with blob_service_client:
            container_client = blob_service_client.get_container_client(
                self._container_name
            )
            blob_client = container_client.get_blob_client(filename)

            index = 0
            block_ids = []
            while True:
                chunk = await source.read(CHUNK_SIZE)
                if not chunk:
                    break

                block_id = f"{index:06}".encode("utf-8").hex()
                await blob_client.stage_block(block_id=block_id, data=chunk)
                block_ids.append(block_id)
                index += 1
            await blob_client.commit_block_list(block_ids)
            log.info(f"File uploaded to azure: {filename}")

    async def get_file(self, filename: str) -> str:
        """Returns the path to the downloaded file."""
        blob_service_client = BlobServiceClient.from_connection_string(
            self._storage_connection_string
        )
        async with blob_service_client:
            container_client = blob_service_client.get_container_client(
                self._container_name
            )
            blob_client = container_client.get_blob_client(filename)

            if not await blob_client.exists():
                raise FileNotFoundError(
                    f"Blob '{filename}' not found in the container.")

            download_stream = await blob_client.download_blob()

            # Create temporary directory and path
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, filename)

            # Save the file in chunks
            async with aiofiles.open(temp_path, 'wb') as f:
                async for chunk in download_stream.chunks():
                    await f.write(chunk)

            return temp_path
