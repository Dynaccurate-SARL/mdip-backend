import pytest
from unittest.mock import AsyncMock, MagicMock, Mock

from src.application.use_cases.drug_catalog.import_task import CatalogImportUseCase
from src.infrastructure.services.confidential_ledger.contract import TransactionData


@pytest.mark.asyncio
async def test_execute_success():
    # Arrange
    drug_catalog_repository_mock = AsyncMock()
    drug_repository_mock = AsyncMock()
    catalog_id = 1
    parser_mock = Mock()
    parser_mock.parse = Mock()
    parser_mock.save_all = AsyncMock()
    session_mock = AsyncMock()
    ledger_service_mock = AsyncMock()
    logger_mock = MagicMock()

    use_case = CatalogImportUseCase(
        drug_catalog_repository=drug_catalog_repository_mock,
        drug_repository=drug_repository_mock,
        catalog_id=catalog_id,
        parser=parser_mock,
        session=session_mock,
        ledger_service=ledger_service_mock,
        logger=logger_mock
    )

    # Act
    await use_case.execute()

    # Assert
    logger_mock.info.assert_any_call(
        f"Catalog import process started for catalog_id={catalog_id}")
    parser_mock.parse.assert_called_once()
    parser_mock.save_all.assert_called_once_with(session_mock, catalog_id)
    logger_mock.info.assert_any_call(
        f"Catalog import completed successfully for catalog_id={catalog_id}")


@pytest.mark.asyncio
async def test_execute_failure():
    # Arrange
    drug_catalog_repository_mock = AsyncMock()
    drug_repository_mock = AsyncMock()
    catalog_id = 1
    parser_mock = Mock()
    parser_mock.parse.side_effect = Exception("Parsing error")
    session_mock = AsyncMock()
    ledger_service_mock = AsyncMock()
    logger_mock = MagicMock()

    use_case = CatalogImportUseCase(
        drug_catalog_repository=drug_catalog_repository_mock,
        drug_repository=drug_repository_mock,
        catalog_id=catalog_id,
        parser=parser_mock,
        session=session_mock,
        ledger_service=ledger_service_mock,
        logger=logger_mock
    )

    # Act
    await use_case.execute()

    # Assert
    logger_mock.info.assert_any_call(
        f"Catalog import process started for catalog_id={catalog_id}")
    parser_mock.parse.assert_called_once()
    logger_mock.error.assert_any_call(
        f"Catalog import failed for catalog_id={catalog_id}")
    logger_mock.exception.assert_called_once()
    drug_repository_mock.delete_all_by_catalog_id.assert_awaited_once_with(
        catalog_id)
