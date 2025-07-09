import pytest
from typing import Any, Generator, TypedDict
from unittest.mock import MagicMock, patch
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from src.infrastructure.services.confidential_ledger.iazure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.contract import TransactionInserted


class AzureLedgerFixture(TypedDict):
    ledger: AzureLedger
    mock_ledger_client: MagicMock


@pytest.fixture
def azure_ledger_fixture() -> Generator[AzureLedgerFixture, Any, None]:
    ledger_url = "https://test-ledger-url"
    certificate_path = "/path/to/certificate"
    mock_ledger_client = MagicMock()

    with patch("src.infrastructure.services.confidential_ledger.iazure_ledger.ConfidentialLedgerClient", return_value=mock_ledger_client):
        ledger = AzureLedger(ledger_url, certificate_path)
        yield {
            "ledger": ledger,
            "mock_ledger_client": mock_ledger_client
        }


def test_insert_transaction(azure_ledger_fixture):
    # Arrange
    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]

    mock_ledger_client.get_current_ledger_entry.return_value = {
        "transactionId": "123e4567-e89b-12d3-a456-426614174000",
        "contents": '{"key": "value"}'
    }

    # Act
    data = {"key": "value"}
    result = ledger.insert_transaction(data)

    # Assert
    mock_ledger_client.create_ledger_entry.assert_called_once()
    assert isinstance(result, TransactionInserted)
    assert result.status == "processing"
    assert result.transaction_id == "123e4567-e89b-12d3-a456-426614174000"


def test_retrieve_transaction_success(azure_ledger_fixture):
    # Arrange
    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]

    mock_ledger_client.begin_get_ledger_entry.return_value.result.return_value = {
        "state": "Ready",
        "entry": {"contents": '{"key": "value"}'}
    }

    # Act
    transaction_id = "123e4567-e89b-12d3-a456-426614174000"
    result = ledger.retrieve_transaction(transaction_id)

    # Assert
    mock_ledger_client.begin_get_ledger_entry.assert_called_once_with(
        str(transaction_id))
    assert isinstance(result, TransactionInserted)
    assert result.status == "ready"
    assert result.transaction_id == transaction_id
    assert result.transaction_data == {"key": "value"}


def test_retrieve_transaction_not_found(azure_ledger_fixture):
    # Arrange
    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]

    mock_ledger_client.begin_get_ledger_entry.side_effect = ResourceNotFoundError()

    # Act
    transaction_id = "123e4567-e89b-12d3-a456-426614174000"
    result = ledger.retrieve_transaction(transaction_id)

    # Assert
    mock_ledger_client.begin_get_ledger_entry.assert_called_once_with(
        str(transaction_id))
    assert result is None


def test_retrieve_transaction_http_error(azure_ledger_fixture):
    # Arrange
    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]

    mock_ledger_client.begin_get_ledger_entry.side_effect = HttpResponseError()

    # Act
    transaction_id = "123e4567-e89b-12d3-a456-426614174000"
    result = ledger.retrieve_transaction(transaction_id)

    # Assert
    mock_ledger_client.begin_get_ledger_entry.assert_called_once_with(
        str(transaction_id))
    assert result is None
