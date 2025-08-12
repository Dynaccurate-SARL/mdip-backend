import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.dto.transaction import MappingTransactionDto
from src.application.use_cases.transaction.get_mapping_transaction import (
    GetMappingTransactionUseCase)

transaction_id = "ce0795d6-7df0-45b5-9f80-0d50d2eba41b"
payload = {
    "status": "created",
    "created_at": "2025-05-19T19:34:36.268798+00:00",
    "filename": "b420400c-ab7a-446b-8e54-8660750b822f_eu-mapping.csv",
    "file_checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "created_at_tz": "UTC",
    "catalog_id": "7330312504196730881",
    "related_catalog_id": "7330314895801454592"
}


@pytest.mark.asyncio
async def test_execute_returns_grouped_transactions():
    # Arrange
    mock_repository = MagicMock()

    mock_transaction_1 = MagicMock()
    mock_transaction_1.transaction_id = transaction_id
    mock_transaction_1.payload = {'mapping_id': "10"} | payload

    mock_transaction_2 = MagicMock()
    mock_transaction_2.transaction_id = transaction_id
    mock_transaction_2.payload = {'mapping_id': "10"} | payload

    mock_transaction_3 = MagicMock()
    mock_transaction_3.transaction_id = transaction_id
    mock_transaction_3.payload = {'mapping_id': "20"} | payload

    mock_repository.get_by_catalog_id = AsyncMock(return_value=[
        mock_transaction_1, mock_transaction_2, mock_transaction_3
    ])
    use_case = GetMappingTransactionUseCase(mock_repository)

    # Act
    result = await use_case.execute(catalog_id=123)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2  # Two groups: mapping_id 10 and 20
    all_ids = sorted([dto.mapping_id for group in result for dto in group])
    assert all_ids == ["10", "10", "20"]
    assert any(len(group) == 2 for group in result)
    assert any(len(group) == 1 for group in result)
    for group in result:
        for dto in group:
            assert isinstance(dto, MappingTransactionDto)


@pytest.mark.asyncio
async def test_execute_with_no_transactions_returns_empty_list():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_by_catalog_id = AsyncMock(return_value=[])
    use_case = GetMappingTransactionUseCase(mock_repository)

    # Act
    result = await use_case.execute(catalog_id=999)

    # Assert
    assert result == []
