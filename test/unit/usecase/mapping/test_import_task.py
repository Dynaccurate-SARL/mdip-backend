import pytest
from fastapi import UploadFile

from unittest.mock import AsyncMock, MagicMock, Mock, patch
from src.application.use_cases.mapping.import_task import MappingImportUseCase
from src.infrastructure.services.pandas_parser.mapping.parse import DrugMappingParse


async def mock_checksum(file: UploadFile, algorithm: str = "sha256"):
    return "checksum123"


@pytest.mark.asyncio
async def test_prepare_task_sets_transaction_data_and_updates_status(monkeypatch):
    # Arrange
    transaction_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    use_case = MappingImportUseCase(
        transaction_repo,
        ledger_service,
        mapping_parser,
        mapping_id,
        central_catalog_id,
        related_catalog_id
    )

    monkeypatch.setattr(
        "src.application.use_cases.mapping.import_task.uploadfile_checksum",
        mock_checksum
    )

    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.csv"
    with patch.object(use_case, "_update_status", new=AsyncMock()) as update_status_mock:
        # Act
        await use_case.prepare_task(file_mock)

        # Assert
        update_status_mock.assert_awaited_once_with('created')
        assert isinstance(use_case._transaction_data, dict)
        assert use_case._transaction_data['filename'] == "test.csv"
        assert use_case._transaction_data['file_checksum'] == "checksum123"
        assert use_case._transaction_data['status'] == "created"
        assert use_case._transaction_data['mapping_id'] == str(mapping_id)
        assert use_case._transaction_data['catalog_id'] == str(
            central_catalog_id)
        assert use_case._transaction_data['related_catalog_id'] == str(
            related_catalog_id)


@pytest.mark.asyncio
async def test_execute_successful_flow(monkeypatch):
    # Arrange
    transaction_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    monkeypatch.setattr(
        "src.application.use_cases.mapping.import_task.mapping_import_taskiq", 
        Mock(kiq=AsyncMock())
    )

    use_case = MappingImportUseCase(
        transaction_repo,
        ledger_service,
        mapping_parser,
        mapping_id,
        central_catalog_id,
        related_catalog_id
    )

    mappings = [[MagicMock(spec=DrugMappingParse)], [
        MagicMock(spec=DrugMappingParse)]]
    mapping_parser.parse.return_value = mappings
    use_case._save_mappings = AsyncMock()
    use_case._update_status = AsyncMock()

    # Act
    await use_case.execute()

    # Assert
    use_case._update_status.assert_any_await('processing')
    use_case._update_status.assert_any_await('completed')
