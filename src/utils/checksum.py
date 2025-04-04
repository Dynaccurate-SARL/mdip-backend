import json
import hashlib
from typing import Dict

from fastapi import UploadFile


def file_checksum(file: UploadFile, algorithm: str = "sha256") -> str:
    """Calculates the checksum of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    while chunk := file.file.read(8192):  # Reads the file in 8 KB chunks
        hash_func.update(chunk)
    file.file.seek(0)  # Resets the file pointer after reading
    return hash_func.hexdigest()


def dict_hash(data: Dict, algorithm: str = "sha256") -> str:
    """Generates a hash from a dictionary using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    # Convert dictionary to JSON string (sorted keys ensure consistency)
    json_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
    # Encode and hash the JSON string
    hash_func.update(json_data.encode("utf-8"))
    return hash_func.hexdigest()
