import json
import hashlib
import aiofiles
from typing import Dict
from fastapi import UploadFile


async def filepath_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """Calculates the checksum of a file at the given path asynchronously."""
    hash_func = hashlib.new(algorithm)
    async with aiofiles.open(file_path, "rb") as file:
        while True:
            chunk = await file.read(8192)
            if not chunk:
                break
            hash_func.update(chunk)
    return hash_func.hexdigest()


async def uploadfile_checksum(file: UploadFile, algorithm: str = "sha256") -> str:
    """Calculates the checksum of an UploadFile instance asynchronously."""
    hash_func = hashlib.new(algorithm)
    while True:
        chunk = await file.read(8192)
        if not chunk:
            break
        hash_func.update(chunk)
    await file.seek(0)  # Reset file pointer after reading
    return hash_func.hexdigest()


def dict_hash(data: Dict, algorithm: str = "sha256") -> str:
    """Generates a hash from a dictionary using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    # Convert dictionary to JSON string (sorted keys ensure consistency)
    json_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
    # Encode and hash the JSON string
    hash_func.update(json_data.encode("utf-8"))
    return hash_func.hexdigest()
