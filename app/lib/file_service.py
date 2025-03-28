import os
import tempfile
import logging as log

from app.config import get_config, UploadStrategy

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient

from typing import Union, Iterable, AnyStr, IO


def __get_azure_container_client() -> ContainerClient:
    blob_service_client = BlobServiceClient.from_connection_string(
        get_config().AZURE_BLOB_STORAGE_CONNECTION_STRING)
    return blob_service_client.get_container_client(get_config().AZURE_BLOB_CONTAINER_NAME)

def upload_file(name: str, file_data: Union[bytes, str, Iterable[AnyStr], IO[AnyStr]]) -> str:
    if (get_config().UPLOAD_STRATEGY == UploadStrategy.AZURE):
        container_client = __get_azure_container_client()
        container_client.upload_blob(name, data=file_data, overwrite=True)

        log.info(f"File uploaded to azure: {name}")
        return name
    
    else:
        if not os.path.exists(get_config().DOCUMENTS_STORAGE_PATH):
            os.makedirs(get_config().DOCUMENTS_STORAGE_PATH)

        destination_file_path = os.path.join(get_config().DOCUMENTS_STORAGE_PATH, name)
        with open(destination_file_path, "wb") as f:
            f.write(file_data)

        log.info(f"File uploaded to disk: {destination_file_path}")
        return destination_file_path

def download_file(name: str) -> str:
    if (get_config().UPLOAD_STRATEGY == UploadStrategy.AZURE):
        temp_dir = tempfile.mkdtemp()

        container_client = __get_azure_container_client()
        file_path = os.path.join(temp_dir, name)
        with open(file_path, mode="wb") as download_file:
            download_file.write(
                container_client.download_blob(name).readall())
        return file_path
        
    else:
        destination_file_path = os.path.join(get_config().DOCUMENTS_STORAGE_PATH, name)
        if not os.path.exists(destination_file_path): 
            raise FileNotFoundError
        return destination_file_path
    
def delete_file(name: str):
    try:
        if (get_config().UPLOAD_STRATEGY == UploadStrategy.AZURE):
            container_client = __get_azure_container_client()
            container_client.delete_blob(name)

        else:
            if not os.path.exists(name):
                os.remove(name)
    except:
        log.error(f"Error to delete. Strategy: {get_config().UPLOAD_STRATEGY}. File path: {name}")