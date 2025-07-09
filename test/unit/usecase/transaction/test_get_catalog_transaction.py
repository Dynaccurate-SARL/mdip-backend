import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.dto.transaction import CatalogTransactionDto
from src.application.use_cases.transaction.get_catalog_transaction import (
    GetCatalogTransactionsUseCase)


@pytest.mark.asyncio
async def test_execute_returns_list_of_catalog_transaction_dto():
    # Arrange
    mock_repository = MagicMock()
    mock_transaction = MagicMock()
    mock_transaction.transaction_id = "f954b9e5-4416-4585-abb3-ec027f2d3478"
    mock_transaction.payload = {
        "status": "completed",
        "created_at": "2025-05-19T19:24:54.212976+00:00",
        "filename": "2cb9a82e-6ef9-45c1-ac31-edb795973555_eu.xlsx",
        "file_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "catalog_id": "7330312504196730881",
        "created_at_tz": "UTC"
    }
    mock_repository.get_all_by_catalog_id = AsyncMock(
        return_value=[mock_transaction])

    use_case = GetCatalogTransactionsUseCase(mock_repository)
    catalog_id = 123

    # Act
    result = await use_case.execute(catalog_id)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CatalogTransactionDto)
    assert result[0].transaction_id == "f954b9e5-4416-4585-abb3-ec027f2d3478"
    assert result[0].status == "completed"
    assert result[0].catalog_id == "7330312504196730881"
    mock_repository.get_all_by_catalog_id.assert_awaited_once_with(catalog_id)


@pytest.mark.asyncio
async def test_execute_returns_empty_list_when_no_transactions():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_all_by_catalog_id = AsyncMock(return_value=[])

    use_case = GetCatalogTransactionsUseCase(mock_repository)
    catalog_id = 456

    # Act
    result = await use_case.execute(catalog_id)

    # Assert
    assert isinstance(result, list)
    assert result == []
    mock_repository.get_all_by_catalog_id.assert_awaited_once_with(catalog_id)
