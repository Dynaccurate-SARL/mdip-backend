import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock
from src.infrastructure.repositories.icatalog_transaction_repository import ICatalogTransactionRepository
from src.domain.entities.ltransactions import CatalogTransaction

@pytest.mark.asyncio
async def test_save_should_add_and_commit_and_refresh():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None

    repository = ICatalogTransactionRepository(mock_session)
    transaction = MagicMock(spec=CatalogTransaction)

    # Act
    result = await repository.save(transaction)

    # Assert
    mock_session.add.assert_called_once_with(transaction)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(transaction)
    assert result == transaction

@pytest.mark.asyncio
async def test_get_by_id_should_return_transaction():
    # Arrange
    mock_session = AsyncMock()
    repo = ICatalogTransactionRepository(mock_session)
    repo.session = mock_session
    transaction = MagicMock(spec=CatalogTransaction)
    mock_session.get.return_value = transaction

    # Act
    result = await repo.get_by_id(1)

    # Assert
    mock_session.get.assert_awaited_once_with(CatalogTransaction, 1)
    assert result == transaction


@pytest.mark.asyncio
async def test_get_all_by_catalog_id_should_return_transactions():
    # Arrange
    mock_session = AsyncMock()
    repo = ICatalogTransactionRepository(mock_session)
    repo.session = mock_session

    catalog_id = 42
    mock_transactions = [MagicMock(spec=CatalogTransaction), MagicMock(spec=CatalogTransaction)]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = mock_transactions

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act
    result = await repo.get_all_by_catalog_id(catalog_id)

    # Assert
    assert result == mock_transactions
    mock_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()