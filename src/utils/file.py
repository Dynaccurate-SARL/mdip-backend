import io
from fastapi import UploadFile


async def read_chunk(file: UploadFile):
    chunk_size = 1024 * 1024  # 1MB
    file_bytes = io.BytesIO()
    while chunk := await file.read(chunk_size):
        file_bytes.write(chunk)
    file_bytes.seek(0)
    return file_bytes
