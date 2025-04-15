import pytest
from typing import TypedDict
from unittest.mock import patch, MagicMock

from src.infrastructure.services.blob_storage.azure_storage import AzureFileService


class AzureServiceMock(TypedDict):
    service: AzureFileService
    mock_container_client: MagicMock


@pytest.fixture
def mock_blob_service_client():
    # Arrange
    with patch("src.infrastructure.services.blob_storage.azure_storage.BlobServiceClient") as mock:
        yield mock


@pytest.fixture
def azure_file_service(mock_blob_service_client) -> AzureServiceMock:
    # Arrange
    mock_container_client = MagicMock()
    mock_blob_service_client\
        .from_connection_string.return_value \
        .get_container_client.return_value = mock_container_client
    return {
        'service': AzureFileService("test-container", "test-connection-string"),
        'mock_container_client': mock_container_client
    }


def test_upload_file(azure_file_service):
    # Arrange
    service = azure_file_service['service']
    mock_container_client = azure_file_service["mock_container_client"]

    # Act
    service.upload_file("test.txt", b"test data")

    # Assert
    mock_container_client.upload_blob.assert_called_once_with(
        "test.txt", data=b"test data", overwrite=True
    )


def test_download_file(azure_file_service):
    # Arrange
    service = azure_file_service['service']
    mock_container_client = azure_file_service["mock_container_client"]
    mock_container_client.download_blob.return_value.readall.return_value = b"test data"

    # Act
    file_path = service.download_file("test.txt")

    # Assert
    mock_container_client.download_blob.assert_called_once_with("test.txt")
    with open(file_path, "rb") as f:
        assert f.read() == b"test data"


def test_delete_file(azure_file_service):
    # Arrange
    service = azure_file_service['service']
    mock_container_client = azure_file_service["mock_container_client"]

    # Act
    service.delete_file("test.txt")

    # Assert
    mock_container_client.delete_blob.assert_called_once_with("test.txt")


def test_upload_file_error_handling(mock_blob_service_client):
    # Arrange
    mock_container_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value.get_container_client.return_value = mock_container_client
    mock_container_client.upload_blob.side_effect = Exception("Upload failed")

    # Act
    service = AzureFileService("test-container", "test-connection-string")

    # Assert
    with pytest.raises(Exception, match="Upload failed"):
        service.upload_file("test.txt", b"test data")


def test_delete_file_error_handling(azure_file_service, caplog):
    # Arrange
    service = azure_file_service['service']
    mock_container_client = azure_file_service["mock_container_client"]
    mock_container_client.delete_blob.side_effect = Exception("Delete failed")

    # Act
    service.delete_file("test.txt")

    # Assert
    mock_container_client.delete_blob.assert_called_once_with("test.txt")
    assert "Error deleting file from Azure" in caplog.text
