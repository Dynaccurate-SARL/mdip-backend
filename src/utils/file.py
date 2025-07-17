import chardet
from io import BytesIO
from pathlib import Path


def _read_sample_or_all(source: BytesIO, sample_size: int = 10_000):
    source.seek(0)
    sample = source.read(sample_size)
    if len(sample) < sample_size:
        source.seek(0)
        sample = source.read()
    source.seek(0)
    return sample


def detect_file_encoding(
        source: BytesIO | str, sample_size: int = 10000) -> str:
    """
    Detects the encoding of a file or byte stream using chardet.

    Args:
        source (BytesIO | str): File path or BytesIO stream.
        sample_size (int): Number of bytes to sample.

    Returns:
        str: Detected encoding. Defaults to 'utf-8' if detection fails.
    """
    def detect_from_bytes(data: bytes) -> str:
        result = chardet.detect(data)
        return result.get("encoding") or "utf-8"

    try:
        if isinstance(source, BytesIO):
            # Move to start, read sample
            data = _read_sample_or_all(source, sample_size)
            return detect_from_bytes(data)
        
        elif isinstance(source, str):
            file_path = Path(source)
            if not file_path.is_file():
                raise FileNotFoundError(f"File not found: {source}")
            with open(file_path, "rb") as file:
                return detect_from_bytes(file.read(sample_size))
        
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")

    except Exception:
        # Log error here if needed
        # Example fallback
        return "utf-8"  # fallback to utf-8
