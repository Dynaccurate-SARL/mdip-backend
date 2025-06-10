from io import BytesIO
from typing import IO
import chardet
from pathlib import Path


def is_valid_path(path_str: str) -> bool:
    """
    Checks if a given string is a valid path to an existing file or directory.

    Parameters:
        path_str (str): The path to check.

    Returns:
        bool: True if the path exists and is a file or directory, False otherwise.
    """
    path = Path(path_str)
    return path.exists()


def detect_file_encoding(
        source: BytesIO | str, sample_size: int = 10000) -> str | None:
    """
    Detects the encoding of a file using the chardet library.

    Parameters:
        source (BytesIO | str): Path to the file or the file object.
        sample_size (int): Number of bytes to read for detection (default: 10000).

    Returns:
        str | None: The detected encoding, or None if detection fails.
    """
    def file_chardet(file: IO):
        raw_data = file.read(sample_size)
        result = chardet.detect(raw_data)
        return result.get('encoding')

    if not is_valid_path(source):
        return chardet.detect(source.read1(sample_size))["encoding"]
    
    try:
        with open(source, 'rb') as file:
            return file_chardet(file)
    except Exception:
        return None
