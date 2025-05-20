import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.repositories.itransaction_repository import (
    ITransactionRepository)


@pytest.mark.asyncio
async def test_get_payload_by_transaction_id_returns_payload():
    # Arrange
    expected_payload = {"foo": "bar"}
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_payload
    mock_session.execute.return_value = mock_result

    transaction_id = uuid4()
    repo = ITransactionRepository(mock_session)

    # Act
    result = await repo.get_payload_by_transaction_id(transaction_id)

    # Assert
    mock_session.execute.assert_awaited_once()
    assert result == expected_payload


@pytest.mark.asyncio
async def test_get_payload_by_transaction_id_returns_none():
    # Arrange
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    transaction_id = uuid4()
    repo = ITransactionRepository(mock_session)

    # Act
    result = await repo.get_payload_by_transaction_id(transaction_id)

    # Assert
    mock_session.execute.assert_awaited_once()
    assert result is None
