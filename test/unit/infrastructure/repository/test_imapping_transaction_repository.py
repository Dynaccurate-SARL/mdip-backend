import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock
from src.domain.entities.ltransactions import MappingTransaction
from src.infrastructure.repositories.imapping_transaction_repository import (
    IMappingTransactionRepository)


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
async def test_get_by_catalog_id_returns_transactions_ordered():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)

    mock_transaction1 = MagicMock(spec=MappingTransaction)
    mock_transaction2 = MagicMock(spec=MappingTransaction)

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [
        mock_transaction1, 
        mock_transaction2
    ]
    mock_result = MagicMock()

    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result
    
    catalog_id = 42
    repo = IMappingTransactionRepository(mock_session)

    # Act
    result = await repo.get_by_catalog_id(catalog_id)

    # Assert
    assert result == [mock_transaction1, mock_transaction2]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_catalog_id_returns_empty_list_when_no_results():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()

    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    catalog_id = 99
    repo = IMappingTransactionRepository(mock_session)

    # Act
    result = await repo.get_by_catalog_id(catalog_id)

    # Assert
    assert result == []
    mock_session.execute.assert_awaited_once()
