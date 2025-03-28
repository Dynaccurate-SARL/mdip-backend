import hashlib

from fastapi import UploadFile


def file_checksum(file: UploadFile):
    """
    Calculate the SHA-256 checksum of a file.

    :param file_path: Path to the file
    :return: The SHA-256 checksum as a hexadecimal string
    """
    sha256 = hashlib.sha256()
    # Read the file in chunks to handle large files efficiently
    for chunk in iter(lambda: file.file.read(4096), b''):
        sha256.update(chunk)
    # Return the checksum as a hexadecimal string
    return sha256.hexdigest()