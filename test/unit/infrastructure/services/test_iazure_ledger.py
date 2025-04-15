import pytest
import sqlalchemy as sq
from typing import Any, Generator, TypedDict
from sqlalchemy.orm import declarative_base
from unittest.mock import AsyncMock, MagicMock, patch
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from src.domain.entities.ledger_transaction import LedgerTransaction
from src.infrastructure.services.confidential_ledger.iazure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.contract import TransactionData, TransactionInserted


class AzureLedgerFixture(TypedDict):
    ledger: AzureLedger
    mock_ledger_client: MagicMock
    mock_lt_repository: AsyncMock


@pytest.fixture
def azure_ledger_fixture() -> Generator[AzureLedgerFixture, Any, None]:
    ledger_url = "https://test-ledger-url"
    certificate_path = "/path/to/certificate"
    mock_lt_repository = AsyncMock()
    mock_ledger_client = MagicMock()

    with patch("src.infrastructure.services.confidential_ledger.iazure_ledger.ConfidentialLedgerClient", return_value=mock_ledger_client):
        ledger = AzureLedger(ledger_url, certificate_path, mock_lt_repository)
        yield {
            "ledger": ledger,
            "mock_ledger_client": mock_ledger_client,
            "mock_lt_repository": mock_lt_repository,
        }


@pytest.mark.asyncio
async def test_insert_transaction(azure_ledger_fixture):
    # Arrange
    Base = declarative_base()

    class TestEntity(Base):
        __tablename__ = 'test_entity'
        id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)

    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]
    mock_lt_repository = azure_ledger_fixture["mock_lt_repository"]

    mock_ledger_client.get_current_ledger_entry.return_value = {
        "transactionId": "12345",
        "contents": '{"key": "value"}'
    }

    data = TransactionData(
        entity_name=TestEntity, entity_id=0, status="created",
        filename="test.csv",  file_checksum='filehash123',
        catatag_hash='cataloghash123'
    )

    # Act
    result = await ledger.insert_transaction(data)

    # Assert
    mock_ledger_client.create_ledger_entry.assert_called_once()
    mock_lt_repository.save.assert_called_once()
    assert isinstance(result, TransactionInserted)
    assert result.transaction_id == "12345"
    assert result.content == {"key": "value"}


@pytest.mark.asyncio
async def test_retrieve_transaction_success(azure_ledger_fixture):
    # Arrange
    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]

    mock_ledger_client.begin_get_ledger_entry.return_value.result.return_value = {
        "state": "Ready",
        "entry": {"contents": '{"key": "value"}'}
    }
    transaction_id = "12345"

    # Act
    result = await ledger.retrieve_transaction(transaction_id)

    # Assert
    mock_ledger_client.begin_get_ledger_entry.assert_called_once_with(
        transaction_id)
    assert isinstance(result, TransactionInserted)
    assert result.transaction_id == transaction_id
    assert result.content == {"key": "value"}


@pytest.mark.asyncio
async def test_retrieve_transaction_not_found(azure_ledger_fixture):
    # Arrange
    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]

    mock_ledger_client.begin_get_ledger_entry.side_effect = ResourceNotFoundError()

    # Act
    result = await ledger.retrieve_transaction("nonexistent-id")

    # Assert
    mock_ledger_client.begin_get_ledger_entry.assert_called_once_with(
        "nonexistent-id")
    assert result is None


@pytest.mark.asyncio
async def test_retrieve_transaction_http_error(azure_ledger_fixture):
    # Arrange
    ledger = azure_ledger_fixture["ledger"]
    mock_ledger_client = azure_ledger_fixture["mock_ledger_client"]

    mock_ledger_client.begin_get_ledger_entry.side_effect = HttpResponseError()

    # Act
    result = await ledger.retrieve_transaction("error-id")

    # Assert
    mock_ledger_client.begin_get_ledger_entry.assert_called_once_with(
        "error-id")
    assert result is None
