import pytest
import time_machine
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.mapping.import_task import MappingImportUseCase
from src.domain.entities.drug_mapping import DrugMapping
from src.infrastructure.services.confidential_ledger.contract import OldTransactionData


@pytest.mark.asyncio
async def test_execute_success():
    # Arrange
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()
    mapping_parser = MagicMock()
    ledger_service = AsyncMock()

    central_catalog_id = 1
    catalog_to_id = 2
    mappings = [
        MagicMock(drug_code="code1", related_drug_code="related_code1"),
        MagicMock(drug_code="code2", related_drug_code="related_code2"),
    ]
    mapping_parser.parse.return_value = [mappings]

    drug_repository.get_by_drug_code_on_catalog_id.return_value = MagicMock(
        _id=1)

    use_case = MappingImportUseCase(
        drug_repository=drug_repository,
        mapping_repository=mapping_repository,
        mapping_parser=mapping_parser,
        ledger_service=ledger_service,
        central_catalog_id=central_catalog_id,
        catalog_to_id=catalog_to_id,
    )

    # Act
    await use_case.execute()

    # Assert
    assert ledger_service.insert_transaction.await_count == 2

    first_call_args = OldTransactionData(
        entity_name="drug_catalogs",
        entity_id=catalog_to_id,
        status="processing",
        data={
            "type": "mapping_import",
            "catalog_central_id": central_catalog_id,
            "catalog_to_id": catalog_to_id,
        },
    )
    second_call_args = OldTransactionData(
        entity_name="drug_catalogs",
        entity_id=catalog_to_id,
        status="completed",
        data={
            "type": "mapping_import",
            "catalog_central_id": central_catalog_id,
            "catalog_to_id": catalog_to_id,
        },
    )

    assert ledger_service.insert_transaction.await_args_list == [
        ((first_call_args,), {}),
        ((second_call_args,), {})
    ]

    assert mapping_repository.save.call_count == len(mappings)
    drug_repository.close_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_failure():
    # Arrange
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()
    mapping_parser = MagicMock()
    ledger_service = AsyncMock()

    central_catalog_id = 1
    catalog_to_id = 2
    mapping_parser.parse.side_effect = Exception("Parsing error")

    use_case = MappingImportUseCase(
        drug_repository=drug_repository,
        mapping_repository=mapping_repository,
        mapping_parser=mapping_parser,
        ledger_service=ledger_service,
        central_catalog_id=central_catalog_id,
        catalog_to_id=catalog_to_id,
    )

    # Act
    await use_case.execute()

    # Assert
    assert ledger_service.insert_transaction.await_count == 2

    first_call_args = OldTransactionData(
        entity_name="drug_catalogs",
        entity_id=catalog_to_id,
        status="processing",
        data={
            "type": "mapping_import",
            "catalog_central_id": central_catalog_id,
            "catalog_to_id": catalog_to_id,
        },
    )
    second_call_args = OldTransactionData(
        entity_name="drug_catalogs",
        entity_id=catalog_to_id,
        status="failed",
        data={
            "type": "mapping_import",
            "catalog_central_id": central_catalog_id,
            "catalog_to_id": catalog_to_id,
        },
    )

    assert ledger_service.insert_transaction.await_args_list == [
        ((first_call_args,), {}),
        ((second_call_args,), {})
    ]

    drug_repository.close_session.assert_awaited_once()
