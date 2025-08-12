import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.infrastructure.services.pandas_parser.mapping.parse import DrugMappingParse
from src.infrastructure.taskiq.mapping_import import task, MappingsTaskData


@pytest.mark.asyncio
@patch("src.infrastructure.taskiq.mapping_import.IDrugRepository")
@patch("src.infrastructure.taskiq.mapping_import.IMappingRepository")
async def test_task_creates_and_logs_mappings(mock_mapping_repo_cls, mock_drug_repo_cls):
    # Arrange
    session = AsyncMock()
    logger = MagicMock()
    data = MappingsTaskData(
        mappings=[
            DrugMappingParse(drug_code="C1", related_drug_code="R1"),
            DrugMappingParse(drug_code="C2", related_drug_code="R2"),
        ],
        central_catalog_id=1,
        related_catalog_id=2,
        mapping_id=42,
    )

    mock_drug_repo = mock_drug_repo_cls.return_value
    mock_mapping_repo = mock_mapping_repo_cls.return_value

    # Simulate drug code maps
    mock_drug_repo.get_drug_map_by_catalog_id = AsyncMock(side_effect=[
        {"C1": 101, "C2": 102},  # central_drug_codes
        {"R1": 201, "R2": 202},  # related_drug_codes
    ])
    # Simulate save: first True (created), then False (already exists)
    mock_mapping_repo.save = AsyncMock(side_effect=[True, False])

    # Act
    await task(session, data, logger=logger)

    # Assert
    assert mock_drug_repo.get_drug_map_by_catalog_id.await_count == 2
    assert mock_mapping_repo.save.await_count == 2

    # Check logging for created and already exists
    logger.info.assert_any_call(
        "42 > Mapping import task started, chunk size 2")
    logger.info.assert_any_call(
        "42 > Creating a hash map with all central drug codes")
    logger.info.assert_any_call(
        "42 > Creating a hash map with all related drug codes")
    logger.info.assert_any_call("42 > Importing mappins")
    logger.info.assert_any_call(
        "42 > Mapping between, central 'C1' to related 'R1' created.")
    logger.warning.assert_any_call(
        "42 > Mapping between, central 'C2' to related 'R2' already exists.")
    logger.info.assert_any_call("42 > Mapping chunk import completed")


@pytest.mark.asyncio
@patch("src.infrastructure.taskiq.mapping_import.IDrugRepository")
@patch("src.infrastructure.taskiq.mapping_import.IMappingRepository")
async def test_task_skips_if_no_ids_found(mock_mapping_repo_cls, mock_drug_repo_cls):
    # Arrange
    session = AsyncMock()
    logger = MagicMock()
    data = MappingsTaskData(
        mappings=[
            DrugMappingParse(drug_code="C1", related_drug_code="R1"),
        ],
        central_catalog_id=1,
        related_catalog_id=2,
        mapping_id=99,
    )

    mock_drug_repo = mock_drug_repo_cls.return_value
    mock_mapping_repo = mock_mapping_repo_cls.return_value

    # Simulate drug code maps with missing codes
    mock_drug_repo.get_drug_map_by_catalog_id = AsyncMock(side_effect=[
        {},  # central_drug_codes
        {},  # related_drug_codes
    ])

    # Act
    await task(session, data, logger=logger)

    # Assert
    logger.info.assert_any_call(
        "99 > Mapping import task started, chunk size 1")
    logger.info.assert_any_call(
        "99 > Creating a hash map with all central drug codes")
    logger.info.assert_any_call(
        "99 > Creating a hash map with all related drug codes")
    logger.info.assert_any_call("99 > Importing mappins")
    logger.info.assert_any_call("99 > Mapping chunk import completed")
