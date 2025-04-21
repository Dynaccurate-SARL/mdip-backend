import os
import pytest
from unittest import mock

from src.infrastructure.services.blob_storage.disk_storage import DiskFileService


@pytest.fixture
def disk_file_service(tmp_path):
    # Arrange
    return DiskFileService(storage_path=str(tmp_path))


def test_upload_file(disk_file_service, tmp_path):
    # Arrange
    file_name = "test_file.txt"
    file_data = b"Sample file content"

    # Act
    uploaded_file_path = disk_file_service.upload_file(file_name, file_data)

    # Assert
    assert os.path.exists(uploaded_file_path)
    assert uploaded_file_path == os.path.join(tmp_path, file_name)
    with open(uploaded_file_path, "rb") as f:
        assert f.read() == file_data


def test_download_file(disk_file_service, tmp_path):
    # Arrange
    file_name = "test_file.txt"
    file_data = b"Sample file content"
    file_path = os.path.join(tmp_path, file_name)

    with open(file_path, "wb") as f:
        f.write(file_data)

    # Act
    downloaded_file_path = disk_file_service.download_file(file_name)

    # Assert
    assert downloaded_file_path == file_path


def test_download_file_not_found(disk_file_service):
    # Act and Assert
    with pytest.raises(FileNotFoundError):
        disk_file_service.download_file("non_existent_file.txt")


def test_delete_file(disk_file_service, tmp_path):
    # Arrange
    file_name = "test_file.txt"
    file_data = b"Sample file content"
    file_path = os.path.join(tmp_path, file_name)

    with open(file_path, "wb") as f:
        f.write(file_data)
    assert os.path.exists(file_path)

    # Act
    disk_file_service.delete_file(file_name)

    # Assert
    assert not os.path.exists(file_path)


def test_delete_file_not_found(disk_file_service):
    # Act and Assert
    # Ensure no exception is raised when trying to delete a non-existent file
    disk_file_service.delete_file("non_existent_file.txt")

    def test_init_creates_storage_path_if_not_exists(tmp_path):
        # Arrange
        storage_path = tmp_path / "storage"
        assert not storage_path.exists()

        # Act
        DiskFileService(storage_path=str(storage_path))

        # Assert
        assert storage_path.exists()


def test_init_does_not_create_storage_path_if_exists():
    # Act
    with mock.patch("os.makedirs") as mock_makedirs:
        DiskFileService(storage_path=str('/storage'))

    # Assert
    mock_makedirs.assert_called_once()


def test_delete_file_logs_error_on_exception(disk_file_service, tmp_path):
    # Arrange
    file_name = "test_file.txt"
    file_data = b"Sample file content"
    file_path = os.path.join(tmp_path, file_name)

    with open(file_path, "wb") as f:
        f.write(file_data)
    assert os.path.exists(file_path)

    with mock.patch("os.remove", side_effect=Exception("Mocked exception")) as mock_remove, \
            mock.patch("src.infrastructure.services.blob_storage.disk_storage.log.error") as mock_log_error:
        # Act
        disk_file_service.delete_file(file_path)

        # Assert
        mock_remove.assert_called_once_with(os.path.join(tmp_path, file_name))
        mock_log_error.assert_called_once()
