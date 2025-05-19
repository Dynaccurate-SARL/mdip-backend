import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock
from src.infrastructure.repositories.imapping_transaction_repository import IMappingTransactionRepository
from src.domain.entities.ltransactions import MappingTransaction


@pytest.mark.asyncio
async def test_save():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None

    transaction = MagicMock(spec=MappingTransaction)
    repo = IMappingTransactionRepository(mock_session)

    # Act
    result = await repo.save(transaction)

    # Assert
    mock_session.add.assert_called_once_with(transaction)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(transaction)
    assert result == transaction


@pytest.mark.asyncio
async def test_get_by_id():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    expected_transaction = MagicMock(spec=MappingTransaction)
    mock_session.get.return_value = expected_transaction

    transaction_id = 123
    repo = IMappingTransactionRepository(mock_session)

    # Act
    result = await repo.get_by_id(transaction_id)

    # Assert
    mock_session.get.assert_awaited_once_with(
        MappingTransaction, transaction_id)
    assert result == expected_transaction


@pytest.mark.asyncio
async def test_get_latest_central_mappings():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)

    expected_transactions = [
        MagicMock(spec=MappingTransaction), MagicMock(spec=MappingTransaction)]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_transactions
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_execute_result

    repo = IMappingTransactionRepository(mock_session)
    catalog_id = 1

    # Act
    result = await repo.get_latest_central_mappings(catalog_id)

    # Assert
    mock_session.execute.assert_awaited()
    assert result == expected_transactions
