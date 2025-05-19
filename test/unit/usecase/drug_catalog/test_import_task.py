import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.application.use_cases.drug_catalog.import_task import CatalogImportUseCase, _created_at

@pytest.mark.asyncio
async def test_prepare_task_updates_status_and_saves_transaction(monkeypatch):
    # Arrange
    mock_drug_catalog_repo = AsyncMock()
    mock_transaction_repo = AsyncMock()
    mock_drug_repo = AsyncMock()
    mock_ledger_service = MagicMock()
    mock_parser = MagicMock()
    mock_session = MagicMock()
    mock_file = MagicMock()
    mock_file.filename = "testfile.csv"
    mock_file_checksum = "checksum123"
    mock_ledger_transaction = MagicMock()
    mock_ledger_transaction.transaction_id = "txid123"
    mock_ledger_service.insert_transaction.return_value = mock_ledger_transaction

    monkeypatch.setattr("src.application.use_cases.drug_catalog.import_task.file_checksum", lambda f: mock_file_checksum)

    use_case = CatalogImportUseCase(
        drug_catalog_repository=mock_drug_catalog_repo,
        transaction_repository=mock_transaction_repo,
        drug_repository=mock_drug_repo,
        ledger_service=mock_ledger_service,
        catalog_id=1,
        parser=mock_parser,
        session=mock_session
    )

    # Act
    await use_case.prepare_task(mock_file)

    # Assert
    mock_drug_catalog_repo.status_update.assert_awaited_once_with(1, 'created')
    mock_transaction_repo.save.assert_awaited_once()
    mock_ledger_service.insert_transaction.assert_called_once()
    assert use_case._transaction_data['status'] == 'created'
    assert use_case._transaction_data['filename'] == "testfile.csv"
    assert use_case._transaction_data['file_checksum'] == mock_file_checksum

@pytest.mark.asyncio
async def test_execute_success(monkeypatch):
    # Arrange
    mock_drug_catalog_repo = AsyncMock()
    mock_transaction_repo = AsyncMock()
    mock_drug_repo = AsyncMock()
    mock_ledger_service = MagicMock()
    mock_parser = MagicMock()
    mock_parser.parse = MagicMock()
    mock_parser.save_all = AsyncMock()
    mock_session = MagicMock()
    catalog_id = 2

    use_case = CatalogImportUseCase(
        drug_catalog_repository=mock_drug_catalog_repo,
        transaction_repository=mock_transaction_repo,
        drug_repository=mock_drug_repo,
        ledger_service=mock_ledger_service,
        catalog_id=catalog_id,
        parser=mock_parser,
        session=mock_session
    )
    use_case._transaction_data = {}

    # Act
    await use_case.execute()

    # Assert
    assert mock_parser.parse.called
    mock_parser.save_all.assert_awaited_once_with(mock_session, catalog_id)
    assert mock_drug_catalog_repo.status_update.await_count >= 2
    mock_drug_catalog_repo.close_session.assert_awaited_once()
    mock_drug_repo.delete_all_by_catalog_id.assert_not_awaited()

@pytest.mark.asyncio
async def test_execute_failure(monkeypatch):
    # Arrange
    mock_drug_catalog_repo = AsyncMock()
    mock_transaction_repo = AsyncMock()
    mock_drug_repo = AsyncMock()
    mock_ledger_service = MagicMock()
    mock_parser = MagicMock()
    mock_parser.parse = MagicMock(side_effect=Exception("parse error"))
    mock_parser.save_all = AsyncMock()
    mock_session = MagicMock()
    catalog_id = 3

    use_case = CatalogImportUseCase(
        drug_catalog_repository=mock_drug_catalog_repo,
        transaction_repository=mock_transaction_repo,
        drug_repository=mock_drug_repo,
        ledger_service=mock_ledger_service,
        catalog_id=catalog_id,
        parser=mock_parser,
        session=mock_session
    )
    use_case._transaction_data = {}

    # Act
    await use_case.execute()

    # Assert
    mock_drug_catalog_repo.status_update.assert_any_await(catalog_id, 'processing')
    mock_drug_catalog_repo.status_update.assert_any_await(catalog_id, 'failed')
    mock_drug_repo.delete_all_by_catalog_id.assert_awaited_once_with(catalog_id)
    mock_drug_catalog_repo.close_session.assert_awaited_once()