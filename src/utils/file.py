from io import BytesIO
from typing import IO
import chardet
from pathlib import Path


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

    path = Path(source)
    if not path.exists():
        return chardet.detect(source.read1(sample_size))["encoding"]

    try:
        with open(source, 'rb') as file:
            return file_chardet(file)
    except Exception:
        return None
