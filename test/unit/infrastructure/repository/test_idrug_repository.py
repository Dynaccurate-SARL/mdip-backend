import pytest
from unittest.mock import AsyncMock
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities import Drug
from src.infrastructure.repositories.idrug_repository import IDrugRepository
from src.infrastructure.repositories.contract import PagedItems

drug = Drug(drug_name="Test Drug", drug_code="TD123",
            catalog_id=1, properties={"hello": "world"})


@pytest.mark.asyncio
async def test_save():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    repository = IDrugRepository(mock_session)
    
    # Act
    result = await repository.save(drug)

    # Assert
    mock_session.add.assert_called_once_with(drug)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(drug)
    assert result.catalog_id == "1"
    assert result == drug


@pytest.mark.asyncio
async def test_get_by_id():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalar_one_or_none.return_value = drug

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IDrugRepository(mock_session)
    
    # Act
    result = await repository.get_by_id(1)

    # Assert
    mock_session.execute.assert_called_once()
    assert result == drug


@pytest.mark.asyncio
async def test_get_all_like_code_or_name():
    # Arrange
    drugs = [drug, drug]
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.all.return_value = drugs

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IDrugRepository(mock_session)
    
    # Act
    result = await repository.get_all_like_code_or_name("Test")

    # Assert
    mock_session.execute.assert_called_once()
    assert len(result) == 2
    assert result == drugs


@pytest.mark.asyncio
async def test_get_total_count():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.scalar.return_value = 10

    repository = IDrugRepository(mock_session)
    
    # Act
    result = await repository.get_total_count(1, "Test")

    # Assert
    mock_session.scalar.assert_called_once()
    assert result == 10


@pytest.mark.asyncio
async def test_get_paginated_by_catalog_id():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.all.return_value = [drug]

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    mock_get_total_count = AsyncMock(return_value=10)

    repository = IDrugRepository(mock_session)
    repository.get_total_count = mock_get_total_count

    # Act
    result = await repository.get_paginated_by_catalog_id(
        page=1, page_size=2, drug_catalog_id=1, name_or_code_filter="Test"
    )

    # Assert
    mock_session.execute.assert_called_once()
    mock_execute_result.scalars.assert_called_once()
    assert isinstance(result, PagedItems)
    assert result.current_page == 1
    assert result.page_size == 2
    assert result.total_count == 10
    assert len(result.items) == 1
    assert result.items == [drug]
