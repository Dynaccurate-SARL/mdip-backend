import io
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile
from src.application.use_cases.mapping.create import MappingCreateUseCase, ResourceNotFound
from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.services.confidential_ledger.contract import TransactionData
from src.utils.checksum import file_checksum


@pytest.mark.asyncio
async def test_execute_success():
    # Arrange
    mock_drug_catalog_repository = AsyncMock()
    mock_ledger_service = AsyncMock()
    use_case = MappingCreateUseCase(
        mock_drug_catalog_repository, mock_ledger_service)

    central_catalog = MagicMock(_id=1)
    related_catalog = MagicMock(_id=2)
    mock_drug_catalog_repository.get_central.return_value = central_catalog
    mock_drug_catalog_repository.get_by_id.return_value = related_catalog

    mock_file = UploadFile(filename="test_file.csv", file=io.BytesIO(b"olar"))

    # Act
    result = await use_case.execute(catalog_to_id=2, file=mock_file)

    # Assert
    assert result.central_catalog_id == central_catalog._id
    assert result.catalog_to_id == related_catalog._id
    mock_drug_catalog_repository.get_central.assert_awaited_once()
    mock_drug_catalog_repository.get_by_id.assert_awaited_once_with(2)
    mock_ledger_service.insert_transaction.assert_awaited_once()
    transaction_data = mock_ledger_service.insert_transaction.call_args[0][0]
    assert isinstance(transaction_data, TransactionData)
    assert transaction_data.data["filename"] == "test_file.csv"
    assert transaction_data.data["file_checksum"] == file_checksum(mock_file)


@pytest.mark.asyncio
async def test_execute_central_catalog_not_found():
    # Arrange
    mock_drug_catalog_repository = AsyncMock()
    mock_ledger_service = AsyncMock()
    use_case = MappingCreateUseCase(
        mock_drug_catalog_repository, mock_ledger_service)

    mock_drug_catalog_repository.get_central.return_value = None
    mock_file = MagicMock(spec=UploadFile)

    # Act & Assert
    with pytest.raises(ResourceNotFound, match="Central catalog not found."):
        await use_case.execute(catalog_to_id=2, file=mock_file)

    mock_drug_catalog_repository.get_central.assert_awaited_once()
    mock_drug_catalog_repository.get_by_id.assert_not_awaited()
    mock_ledger_service.insert_transaction.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_related_catalog_not_found():
    # Arrange
    mock_drug_catalog_repository = AsyncMock()
    mock_ledger_service = AsyncMock()
    use_case = MappingCreateUseCase(
        mock_drug_catalog_repository, mock_ledger_service)

    central_catalog = MagicMock(_id=1)
    mock_drug_catalog_repository.get_central.return_value = central_catalog
    mock_drug_catalog_repository.get_by_id.return_value = None
    mock_file = MagicMock(spec=UploadFile)

    # Act & Assert
    with pytest.raises(ResourceNotFound, match="Related catalog not found."):
        await use_case.execute(catalog_to_id=2, file=mock_file)

    mock_drug_catalog_repository.get_central.assert_awaited_once()
    mock_drug_catalog_repository.get_by_id.assert_awaited_once_with(2)
    mock_ledger_service.insert_transaction.assert_not_awaited()
