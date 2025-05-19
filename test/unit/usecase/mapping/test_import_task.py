from fastapi import UploadFile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.application.use_cases.mapping.import_task import MappingImportUseCase, _created_at
from src.domain.entities.drug_catalog import TaskStatus
from src.domain.entities.drug_mapping import DrugMapping
from src.domain.entities.ltransactions import MappingTransactionData


@pytest.mark.asyncio
async def test_prepare_task_sets_transaction_data_and_updates_status():
    # Arrange
    drug_repo = AsyncMock()
    transaction_repo = AsyncMock()
    mapping_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    use_case = MappingImportUseCase(
        drug_repo, transaction_repo, mapping_repo,
        ledger_service, mapping_parser,
        mapping_id, central_catalog_id, related_catalog_id
    )

    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.csv"
    with patch("src.application.use_cases.mapping.import_task.file_checksum", return_value="abc123"), \
            patch.object(use_case, "_update_status", new=AsyncMock()) as update_status_mock:
        # Act
        await use_case.prepare_task(file_mock)

        # Assert
        update_status_mock.assert_awaited_once_with('created')
        assert isinstance(use_case._transaction_data, dict)
        assert use_case._transaction_data['filename'] == "test.csv"
        assert use_case._transaction_data['file_checksum'] == "abc123"
        assert use_case._transaction_data['status'] == "created"
        assert use_case._transaction_data['mapping_id'] == str(mapping_id)
        assert use_case._transaction_data['catalog_id'] == str(
            central_catalog_id)
        assert use_case._transaction_data['related_catalog_id'] == str(
            related_catalog_id)


@pytest.mark.asyncio
async def test_execute_successful_flow():
    # Arrange
    drug_repo = AsyncMock()
    transaction_repo = AsyncMock()
    mapping_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    use_case = MappingImportUseCase(
        drug_repo, transaction_repo, mapping_repo,
        ledger_service, mapping_parser,
        mapping_id, central_catalog_id, related_catalog_id
    )

    mappings = [[MagicMock(spec=DrugMapping)], [MagicMock(spec=DrugMapping)]]
    mapping_parser.parse.return_value = mappings
    use_case._save_mappings = AsyncMock()
    use_case._update_status = AsyncMock()
    drug_repo.close_session = AsyncMock()

    # Act
    await use_case.execute()

    # Assert
    use_case._update_status.assert_any_await('processing')
    use_case._save_mappings.assert_any_await(mappings[0])
    use_case._save_mappings.assert_any_await(mappings[1])
    use_case._update_status.assert_any_await('completed')
    drug_repo.close_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_handles_exception_and_deletes_mappings():
    # Arrange
    drug_repo = AsyncMock()
    transaction_repo = AsyncMock()
    mapping_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    use_case = MappingImportUseCase(
        drug_repo, transaction_repo, mapping_repo,
        ledger_service, mapping_parser,
        mapping_id, central_catalog_id, related_catalog_id
    )

    mapping_parser.parse.side_effect = Exception("parse error")
    use_case._save_mappings = AsyncMock()
    use_case._update_status = AsyncMock()
    mapping_repo.delete_all_by_mapping_id = AsyncMock()
    drug_repo.close_session = AsyncMock()

    # Act
    await use_case.execute()

    # Assert
    use_case._update_status.assert_any_await('processing')
    use_case._update_status.assert_any_await('failed')
    mapping_repo.delete_all_by_mapping_id.assert_awaited_once_with(mapping_id)
    drug_repo.close_session.assert_awaited_once()


@pytest.mark.asyncio
async def test__save_mappings_saves_when_drugs_found():
    # Arrange
    drug_repo = AsyncMock()
    transaction_repo = AsyncMock()
    mapping_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    use_case = MappingImportUseCase(
        drug_repo, transaction_repo, mapping_repo,
        ledger_service, mapping_parser,
        mapping_id, central_catalog_id, related_catalog_id
    )

    mapping = MagicMock(spec=DrugMapping)
    mapping.drug_code = "A"
    mapping.related_drug_code = "B"
    central_drug = MagicMock()
    central_drug._id = 10
    related_drug = MagicMock()
    related_drug._id = 20

    drug_repo.get_by_drug_code_on_catalog_id.side_effect = [
        central_drug, related_drug]
    mapping_repo.save = AsyncMock()

    # Act
    await use_case._save_mappings([mapping])

    # Assert
    drug_repo.get_by_drug_code_on_catalog_id.assert_any_await(
        central_catalog_id, "A")
    drug_repo.get_by_drug_code_on_catalog_id.assert_any_await(
        related_catalog_id, "B")
    mapping_repo.save.assert_awaited()


@pytest.mark.asyncio
async def test__save_mappings_skips_when_central_drug_not_found():
    # Arrange
    drug_repo = AsyncMock()
    transaction_repo = AsyncMock()
    mapping_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    use_case = MappingImportUseCase(
        drug_repo, transaction_repo, mapping_repo,
        ledger_service, mapping_parser,
        mapping_id, central_catalog_id, related_catalog_id
    )

    mapping = MagicMock(spec=DrugMapping)
    mapping.drug_code = "A"
    mapping.related_drug_code = "B"
    drug_repo.get_by_drug_code_on_catalog_id.return_value = None
    mapping_repo.save = AsyncMock()

    # Act
    await use_case._save_mappings([mapping])

    # Assert
    drug_repo.get_by_drug_code_on_catalog_id.assert_awaited_once_with(
        central_catalog_id, "A")
    mapping_repo.save.assert_not_awaited()


@pytest.mark.asyncio
async def test__update_status_saves_transaction():
    # Arrange
    drug_repo = AsyncMock()
    transaction_repo = AsyncMock()
    mapping_repo = AsyncMock()
    ledger_service = MagicMock()
    mapping_parser = MagicMock()
    mapping_id = 1
    central_catalog_id = 2
    related_catalog_id = 3

    use_case = MappingImportUseCase(
        drug_repo, transaction_repo, mapping_repo,
        ledger_service, mapping_parser,
        mapping_id, central_catalog_id, related_catalog_id
    )

    use_case._transaction_data = {
        'status': 'created',
        'created_at': '2024-01-01T00:00:00Z'
    }
    ledger_transaction = MagicMock()
    ledger_transaction.transaction_id = "txid"
    ledger_service.insert_transaction.return_value = ledger_transaction
    transaction_repo.save = AsyncMock()

    # Act
    await use_case._update_status('processing')

    # Assert
    assert use_case._transaction_data['status'] == 'processing'
    assert 'created_at' in use_case._transaction_data
    ledger_service.insert_transaction.assert_called_once_with(
        use_case._transaction_data)
    transaction_repo.save.assert_awaited()
