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
async def test_get_latest_by_catalog_id_should_return_latest_transaction():
    # Arrange
    mock_session = AsyncMock()
    repo = ICatalogTransactionRepository(mock_session)
    repo.session = mock_session
    catalog_id = 123
    transaction = MagicMock(spec=CatalogTransaction)
    mock_scalar = MagicMock()
    mock_scalar.scalar_one_or_none.return_value = transaction
    mock_session.execute.return_value = mock_scalar

    # Act
    result = await repo.get_latest_by_catalog_id(catalog_id)

    # Assert
    mock_session.execute.assert_awaited()
    mock_scalar.scalar_one_or_none.assert_called_once()
    assert result == transaction