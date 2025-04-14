import pytest
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.iledger_transaction_repository import ILedgerTransactionRepository
from src.domain.entities.ledger_transaction import LedgerTransaction

ledger_transaction = LedgerTransaction(
    transaction_id='001', entity_name=DrugCatalog,
    entity_id=1, content={"hello": "world"})


@pytest.mark.asyncio
async def test_save_transaction():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    
    repository = ILedgerTransactionRepository(mock_session)

    # Act
    result = await repository.save(ledger_transaction)

    # Assert
    mock_session.add.assert_called_once_with(ledger_transaction)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(ledger_transaction)
    assert result == ledger_transaction


@pytest.mark.asyncio
async def test_get_by_transaction_id_found():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalar_one_or_none.return_value = ledger_transaction

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = ILedgerTransactionRepository(mock_session)

    # Act
    result = await repository.get_by_transaction_id(1)

    # Assert
    mock_session.execute.assert_called_once()
    assert result == ledger_transaction


@pytest.mark.asyncio
async def test_get_by_transaction_id_not_found():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = ILedgerTransactionRepository(mock_session)

    # Act
    result = await repository.get_by_transaction_id(1)

    # Assert
    mock_session.execute.assert_called_once()
    assert result is None
