import pytest
from io import BytesIO
from fastapi import UploadFile
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.drug_catalog.create import DrugCatalogCreateUseCase
from src.application.dto.drug_catalog_dto import DrugCatalogCreateDto, DrugCatalogCreatedDto
from src.domain.entities.drug_catalog import DrugCatalog
from src.utils.exc import ConflictErrorCode


test_file_c = b"Test file content"
test_file = UploadFile(filename="test_file.txt", file=BytesIO(test_file_c))


@pytest.mark.asyncio
async def test_execute_creates_drug_catalog_and_sends_to_ledger():
    # Arrange
    mock_repository = AsyncMock()
    mock_ledger_service = AsyncMock()
    use_case = DrugCatalogCreateUseCase(mock_repository, mock_ledger_service)

    data = DrugCatalogCreateDto(
        name="Test Catalog",
        country="FR",
        version="1.0",
        notes="Test Notes",
        is_central=False,
        file=test_file
    )

    mock_drug_catalog = DrugCatalog._mock()
    mock_repository.save.return_value = mock_drug_catalog

    mock_transaction = MagicMock(transaction_id="txn_123")
    mock_ledger_service.insert_transaction.return_value = mock_transaction

    # Act
    result = await use_case.execute(data)

    # Assert
    mock_repository.save.assert_called_once()
    mock_ledger_service.insert_transaction.assert_called_once()
    assert isinstance(result, DrugCatalogCreatedDto)
    assert result.transaction_id == "txn_123"


@pytest.mark.asyncio
async def test_execute_raises_conflict_error_if_central_catalog_exists():
    # Arrange
    mock_repository = AsyncMock()
    mock_ledger_service = AsyncMock()
    use_case = DrugCatalogCreateUseCase(mock_repository, mock_ledger_service)

    data = DrugCatalogCreateDto(
        name="Central Catalog",
        country="FR",
        version="1.0",
        notes="Test Notes",
        is_central=True,
        file=test_file  # Use UploadFile object
    )

    mock_repository.get_central.return_value = True

    # Act & Assert
    with pytest.raises(ConflictErrorCode, match="Central drug catalog already exists."):
        await use_case.execute(data)

    mock_repository.get_central.assert_called_once()
    mock_repository.save.assert_not_called()
    mock_ledger_service.insert_transaction.assert_not_called()
