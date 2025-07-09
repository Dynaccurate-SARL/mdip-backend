import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.dto.transaction import TransactionDto
from src.application.use_cases.transaction.verify_transaction import (
    VerifyTransactionUseCase
)

transaction_id = "ce0795d6-7df0-45b5-9f80-0d50d2eba41b"
payload = {
    "status": "created",
    "created_at": "2025-05-19T19:34:36.268798+00:00",
    "filename": "b420400c-ab7a-446b-8e54-8660750b822f_eu-mapping.csv",
    "file_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "created_at_tz": "UTC",
    "mapping_id": "7330314956379787264",
    "catalog_id": "7330312504196730881",
    "related_catalog_id": "7330314895801454592"
}
payload_hash = "5000d4307fb73e5d2b46afb789d4606c99c39ffa26f4510fa7eddb1d02af993e"


@pytest.mark.asyncio
async def test_execute_returns_invalid_when_payload_is_none():
    # Arrange
    t_repository = AsyncMock()
    t_repository.get_payload_by_transaction_id.return_value = None
    ledger_service = MagicMock()
    use_case = VerifyTransactionUseCase(t_repository, ledger_service)

    # Act
    result = await use_case.execute(transaction_id)

    # Assert
    assert isinstance(result, TransactionDto)
    assert result.valid is False


@pytest.mark.asyncio
async def test_execute_returns_invalid_when_transaction_is_none():
    # Arrange
    t_repository = AsyncMock()
    t_repository.get_payload_by_transaction_id.return_value = payload
    ledger_service = MagicMock()
    ledger_service.retrieve_transaction.return_value = None
    use_case = VerifyTransactionUseCase(t_repository, ledger_service)

    # Act
    result = await use_case.execute(transaction_id)

    # Assert
    assert isinstance(result, TransactionDto)
    assert result.valid is False


@pytest.mark.asyncio
async def test_execute_returns_valid_when_hash_matches(monkeypatch):
    # Arrange
    expected_hash = payload_hash

    t_repository = AsyncMock()
    t_repository.get_payload_by_transaction_id.return_value = payload

    transaction_mock = MagicMock()
    transaction_mock.transaction_data = {'hash': expected_hash}

    ledger_service = MagicMock()
    ledger_service.retrieve_transaction.return_value = transaction_mock

    # Patch dict_hash to return the expected hash
    monkeypatch.setattr(
        "src.application.use_cases.transaction.verify_transaction.dict_hash",
        lambda x: expected_hash
    )

    use_case = VerifyTransactionUseCase(t_repository, ledger_service)

    # Act
    result = await use_case.execute(transaction_id)

    # Assert
    assert isinstance(result, TransactionDto)
    assert result.valid is True


@pytest.mark.asyncio
async def test_execute_returns_invalid_when_hash_does_not_match(monkeypatch):
    # Arrange
    ledger_hash = "different_hash"

    t_repository = AsyncMock()
    t_repository.get_payload_by_transaction_id.return_value = payload

    transaction_mock = MagicMock()
    transaction_mock.transaction_data = {'hash': ledger_hash}

    ledger_service = MagicMock()
    ledger_service.retrieve_transaction.return_value = transaction_mock

    # Patch dict_hash to return a different hash
    monkeypatch.setattr(
        "src.application.use_cases.transaction.verify_transaction.dict_hash",
        lambda x: payload_hash
    )

    use_case = VerifyTransactionUseCase(t_repository, ledger_service)

    # Act
    result = await use_case.execute(transaction_id)

    # Assert
    assert isinstance(result, TransactionDto)
    assert result.valid is False
