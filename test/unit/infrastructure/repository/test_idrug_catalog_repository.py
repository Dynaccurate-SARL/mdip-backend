import pytest
from unittest.mock import AsyncMock
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import PagedItems
from src.infrastructure.repositories.idrug_catalog_repository import IDrugCatalogRepository

drug_catalog = DrugCatalog(
    name="Test Catalog", country="PA", version="1.0", 
    notes="Test notes", is_central=True)


@pytest.mark.asyncio
async def test_save():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    repository = IDrugCatalogRepository(mock_session)

    # Act
    result = await repository.save(drug_catalog)

    # Assert
    mock_session.add.assert_called_once_with(drug_catalog)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(drug_catalog)
    assert result == drug_catalog


@pytest.mark.asyncio
async def test_get_by_id():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.one_or_none.return_value = drug_catalog

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IDrugCatalogRepository(mock_session)

    # Act
    result = await repository.get_by_id(1)

    # Assert
    mock_session.execute.assert_called_once()
    mock_execute_result.scalars.assert_called_once()
    mock_execute_result.scalars.return_value.one_or_none.assert_called_once()
    assert result == drug_catalog


@pytest.mark.asyncio
async def test_status_update_processing():
    # Arrange
    mock_execute = AsyncMock(spec=Result)
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute

    repository = IDrugCatalogRepository(mock_session)

    # Act
    result = await repository.status_update(1, 'processing')

    # Assert
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_status_update_failed():
    # Arrange
    mock_execute = AsyncMock(spec=Result)
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute

    repository = IDrugCatalogRepository(mock_session)

    # Act
    result = await repository.status_update(1, 'failed')

    # Assert
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_total_count():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.scalar.return_value = 10

    repository = IDrugCatalogRepository(mock_session)

    # Act
    result = await repository.get_total_count(name_filter="Test")

    # Assert
    mock_session.scalar.assert_called_once()
    assert result == 10


@pytest.mark.asyncio
async def test_get_central_catalog():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.one_or_none.return_value = drug_catalog

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IDrugCatalogRepository(mock_session)

    # Act
    result = await repository.get_central()

    # Assert
    mock_session.execute.assert_called_once()
    mock_execute_result.scalars.assert_called_once()
    mock_execute_result.scalars.return_value.one_or_none.assert_called_once()
    assert result == drug_catalog


@pytest.mark.asyncio
async def test_get_paginated():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.all.return_value = [drug_catalog]

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    mock_get_total_count = AsyncMock(return_value=10)

    repository = IDrugCatalogRepository(mock_session)
    repository.get_total_count = mock_get_total_count

    # Act
    result = await repository.get_paginated(
        page=1, page_size=5, name_filter="Test")

    # Assert
    mock_session.execute.assert_called_once()
    mock_execute_result.scalars.assert_called_once()
    mock_execute_result.scalars.return_value.all.assert_called_once()
    repository.get_total_count.assert_called_once_with("Test")
    assert isinstance(result, PagedItems)
    assert result.current_page == 1
    assert result.page_size == 5
    assert result.total_count == 10
    assert len(result.items) == 1
    assert result.items[0] == drug_catalog
