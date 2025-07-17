import os
import pytest
from unittest import mock

from src.infrastructure.services.blob_storage.disk_storage import DiskFileService
from fastapi import UploadFile
from io import BytesIO

from src.utils import file


@pytest.fixture
def disk_file_service(tmp_path):
    # Arrange
    return DiskFileService(storage_path=str(tmp_path))


@pytest.mark.asyncio
async def test_upload_file(disk_file_service, tmp_path):
    # Arrange
    file_name = "test_file.txt"
    file_data = b"Sample file content"
    source = UploadFile(filename=file_name, file=BytesIO(file_data))

    # Act
    uploaded_file_path = await disk_file_service.upload_file(
        file_name, source)

    # Assert
    assert os.path.exists(uploaded_file_path)
    assert uploaded_file_path == os.path.join(tmp_path, file_name)
    with open(uploaded_file_path, "rb") as f:
        assert f.read() == file_data


@pytest.mark.asyncio
async def test_get_file(disk_file_service, tmp_path):
    # Arrange
    file_name = "test_file.txt"
    file_data = b"Sample file content"
    file_path = os.path.join(tmp_path, file_name)

    with open(file_path, "wb") as f:
        f.write(file_data)

    # Act
    downloaded_file_path = await disk_file_service.get_file(file_name)

    # Assert
    assert downloaded_file_path == file_path


@pytest.mark.asyncio
async def test_get_file_not_found(disk_file_service):
    # Act and Assert
    with pytest.raises(FileNotFoundError):
        await disk_file_service.get_file("non_existent_file.txt")


@pytest.mark.asyncio
async def test_init_does_not_create_storage_path_if_exists():
    # Act
    with mock.patch("os.makedirs") as mock_makedirs:
        DiskFileService(storage_path=str('/storage'))

    # Assert
    mock_makedirs.assert_called_once()
