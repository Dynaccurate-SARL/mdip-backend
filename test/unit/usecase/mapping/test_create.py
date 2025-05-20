import pytest

from src.utils.exc import ResourceNotFound
from unittest.mock import AsyncMock, MagicMock, patch
from src.application.use_cases.mapping.create import MappingCheckUseCase, MappingCheck


@pytest.mark.asyncio
async def test_execute_success(monkeypatch):
    # Arrange
    mock_repo = MagicMock()
    central_catalog = MagicMock()
    central_catalog._id = 123
    related_catalog = MagicMock()
    mock_repo.get_central = AsyncMock(return_value=central_catalog)
    mock_repo.get_by_id = AsyncMock(return_value=related_catalog)
    use_case = MappingCheckUseCase(mock_repo)
    fake_mapping_id = 999

    monkeypatch.setattr(
        "src.application.use_cases.mapping.create.generate_snowflake_id",
        lambda: fake_mapping_id
    )

    # Act
    result = await use_case.execute(456)

    # Assert
    assert isinstance(result, MappingCheck)
    assert result.mapping_id == fake_mapping_id
    assert result.central_catalog_id == 123
    mock_repo.get_central.assert_awaited_once()
    mock_repo.get_by_id.assert_awaited_once_with(456)


@pytest.mark.asyncio
async def test_execute_central_catalog_not_found():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_central = AsyncMock(return_value=None)
    use_case = MappingCheckUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(ResourceNotFound, match="Central catalog not found."):
        await use_case.execute(456)
    mock_repo.get_central.assert_awaited_once()
    mock_repo.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_execute_related_catalog_not_found():
    # Arrange
    mock_repo = MagicMock()
    central_catalog = MagicMock()
    central_catalog._id = 123
    mock_repo.get_central = AsyncMock(return_value=central_catalog)
    mock_repo.get_by_id = AsyncMock(return_value=None)
    use_case = MappingCheckUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(ResourceNotFound, match="Related catalog not found."):
        await use_case.execute(456)
    mock_repo.get_central.assert_awaited_once()
    mock_repo.get_by_id.assert_awaited_once_with(456)
