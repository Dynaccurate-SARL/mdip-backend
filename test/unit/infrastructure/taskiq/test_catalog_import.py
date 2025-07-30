import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.infrastructure.taskiq.catalog_import import task, ParseTaskData


@pytest.mark.asyncio
@patch("src.infrastructure.taskiq.catalog_import.get_file", new_callable=AsyncMock)
@patch("src.infrastructure.taskiq.catalog_import.drug_parser_factory")
@patch("src.infrastructure.taskiq.catalog_import.IDrugCatalogRepository")
@patch("src.infrastructure.taskiq.catalog_import.ICatalogTransactionRepository")
@patch("src.infrastructure.taskiq.catalog_import.IDrugRepository")
@patch("src.infrastructure.taskiq.catalog_import.ledger_builder")
@patch("src.infrastructure.taskiq.catalog_import.CatalogImportUseCase")
async def test_task_happy_path(
    mock_use_case,
    mock_ledger_builder,
    mock_drug_repository,
    mock_transaction_repository,
    mock_catalog_repository,
    mock_drug_parser_factory,
    mock_get_file,
):
    # Arrange
    session = MagicMock()
    data = ParseTaskData(catalog_id=1, filename="file.csv", parser="EU")
    config = MagicMock()
    mock_get_file.return_value = "mocked/path/file.csv"
    mock_parser_instance = MagicMock()
    mock_drug_parser_factory.return_value = MagicMock(
        return_value=mock_parser_instance)
    mock_ledger_service = MagicMock()
    mock_ledger_builder.return_value = mock_ledger_service
    mock_use_case_instance = AsyncMock()
    mock_use_case.return_value = mock_use_case_instance

    # Act
    await task(session, data, config)

    # Assert
    mock_get_file.assert_awaited_once_with("file.csv", config)
    mock_drug_parser_factory.assert_called_once_with("EU")
    mock_catalog_repository.assert_called_once_with(session)
    mock_transaction_repository.assert_called_once_with(session)
    mock_drug_repository.assert_called_once_with(session)
    mock_ledger_builder.assert_called_once()
    mock_use_case.assert_called_once_with(
        drug_catalog_repository=mock_catalog_repository.return_value,
        transaction_repository=mock_transaction_repository.return_value,
        drug_repository=mock_drug_repository.return_value,
        ledger_service=mock_ledger_service,
        catalog_id=1,
        parser=mock_parser_instance,
        session=session,
    )
    mock_use_case_instance.prepare_transaction_data.assert_awaited_once_with(
        "file.csv", "mocked/path/file.csv")
    mock_use_case_instance.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.infrastructure.taskiq.catalog_import.get_file", new_callable=AsyncMock)
@patch("src.infrastructure.taskiq.catalog_import.drug_parser_factory")
@patch("src.infrastructure.taskiq.catalog_import.IDrugCatalogRepository")
@patch("src.infrastructure.taskiq.catalog_import.ICatalogTransactionRepository")
@patch("src.infrastructure.taskiq.catalog_import.IDrugRepository")
@patch("src.infrastructure.taskiq.catalog_import.ledger_builder")
@patch("src.infrastructure.taskiq.catalog_import.CatalogImportUseCase")
async def test_task_raises_when_get_file_fails(
    mock_use_case,
    mock_ledger_builder,
    mock_drug_repository,
    mock_transaction_repository,
    mock_catalog_repository,
    mock_drug_parser_factory,
    mock_get_file,
):
    # Arrange
    session = MagicMock()
    data = ParseTaskData(catalog_id=2, filename="missing.csv", parser="EU")
    config = MagicMock()
    mock_get_file.side_effect = Exception("File not found")

    # Act & Assert
    with pytest.raises(Exception, match="File not found"):
        await task(session, data, config)
    mock_get_file.assert_awaited_once_with("missing.csv", config)
