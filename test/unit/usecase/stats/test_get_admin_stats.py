import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.stats.get_admin_stats import GetAdminStatsUseCase
from src.application.dto.stats_dto import AdminStatsDto, StatsKind


@pytest.mark.asyncio
async def test_execute_central():
    # Arrange
    drug_catalog_repository = AsyncMock()
    mapping_repository = AsyncMock()
    drug_catalog_repository.get_central.return_value = AsyncMock(
        status="created")
    use_case = GetAdminStatsUseCase(
        drug_catalog_repository, mapping_repository)

    # Act
    result = await use_case.execute('central')

    # Assert
    assert isinstance(result, AdminStatsDto)
    assert result.central_catalog.status == "created"
    drug_catalog_repository.get_central.assert_awaited_once()
    mapping_repository.get_total_count.assert_not_called()


@pytest.mark.asyncio
async def test_execute_total_catalogs():
    # Arrange
    drug_catalog_repository = AsyncMock()
    mapping_repository = AsyncMock()
    drug_catalog_repository.get_total_count.return_value = 10
    use_case = GetAdminStatsUseCase(
        drug_catalog_repository, mapping_repository)

    # Act
    result = await use_case.execute('total_catalogs')

    # Assert
    assert isinstance(result, AdminStatsDto)
    assert result.total_catalogs.total == 10
    drug_catalog_repository.get_total_count.assert_awaited_once()
    mapping_repository.get_total_count.assert_not_called()


@pytest.mark.asyncio
async def test_execute_total_mappings():
    # Arrange
    drug_catalog_repository = AsyncMock()
    mapping_repository = AsyncMock()
    mapping_repository.get_total_count.return_value = 5
    use_case = GetAdminStatsUseCase(
        drug_catalog_repository, mapping_repository)

    # Act
    result = await use_case.execute('total_mappins')

    # Assert
    assert isinstance(result, AdminStatsDto)
    assert result.total_mappins.total == 5
    mapping_repository.get_total_count.assert_awaited_once()
    drug_catalog_repository.get_total_count.assert_not_called()


@pytest.mark.asyncio
async def test_execute_all_stats():
    # Arrange
    drug_catalog_repository = AsyncMock()
    mapping_repository = AsyncMock()
    drug_catalog_repository.get_central.return_value = AsyncMock(
        status="completed")
    drug_catalog_repository.get_total_count.return_value = 10
    mapping_repository.get_total_count.return_value = 5
    use_case = GetAdminStatsUseCase(
        drug_catalog_repository, mapping_repository)

    # Act
    result = await use_case.execute('all')

    # Assert
    assert isinstance(result, AdminStatsDto)
    assert result.central_catalog.status == "completed"
    assert result.total_catalogs.total == 10
    assert result.total_mappins.total == 5
    drug_catalog_repository.get_central.assert_awaited_once()
    drug_catalog_repository.get_total_count.assert_awaited_once()
    mapping_repository.get_total_count.assert_awaited_once()
