from typing import Literal
from pydantic import model_validator

UploadStrategy = Literal['DISK', 'AZURE']


class BlobEnvs:
    UPLOAD_STRATEGY: UploadStrategy
    # strategy: disk
    DOCUMENTS_STORAGE_PATH: str | None = 'documents'
    # strategy: azure
    AZURE_BLOB_CONTAINER_NAME: str | None = None
    AZURE_BLOB_STORAGE_CONNECTION_STRING: str | None = None

    @model_validator(mode='after')
    def check_upload_strategy(cls, values: 'BlobEnvs') -> 'BlobEnvs':
        strategy = values.UPLOAD_STRATEGY

        if strategy == "DISK":
            required = ["DOCUMENTS_STORAGE_PATH"]
            for field in required:
                if not getattr(values, field):
                    raise ValueError(
                        f"'{field}' is required when 'UPLOAD_STRATEGY' is 'DISK'\n")

        if strategy == "AZURE":
            required = ["AZURE_BLOB_CONTAINER_NAME",
                        "AZURE_BLOB_STORAGE_CONNECTION_STRING"]
            for field in required:
                if not getattr(values, field):
                    raise ValueError(
                        f"'{field}' is required when 'UPLOAD_STRATEGY' is 'AZURE'\n")
        return values
