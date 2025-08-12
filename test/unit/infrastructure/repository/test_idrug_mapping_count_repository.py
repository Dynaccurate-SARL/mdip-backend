import pytest
from unittest.mock import AsyncMock
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.idrug_mapping_count_repository import IDrugMappingCountViewInterface
from src.domain.entities.drug_mapping_count_view import DrugMappingCountView


@pytest.mark.asyncio
async def test_get_all_like_code_or_name_with_filter_and_limit():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.all.return_value = [
        DrugMappingCountView(drug_name="TestDrug", drug_code="TD123")]
    
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IDrugMappingCountViewInterface(mock_session)

    # Act
    result = await repository.get_all_like_code_or_name("Test", 1)

    # Assert
    mock_session.execute.assert_called_once()
    assert len(result) == 1
    assert result[0].drug_name == "TestDrug"
    assert result[0].drug_code == "TD123"


@pytest.mark.asyncio
async def test_get_all_like_code_or_name_without_filter():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.all.return_value = [
        DrugMappingCountView(drug_name="TestDrug", drug_code="TD123")]
    
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IDrugMappingCountViewInterface(mock_session)

    # Act
    result = await repository.get_all_like_code_or_name("", 0)

    # Assert
    mock_session.execute.assert_called_once()
    assert len(result) == 1
    assert result[0].drug_name == "TestDrug"
    assert result[0].drug_code == "TD123"


@pytest.mark.asyncio
async def test_get_all_like_code_or_name_with_limit_only():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalars.return_value.all.return_value = [
        DrugMappingCountView(drug_name="TestDrug", drug_code="TD123")]
    
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IDrugMappingCountViewInterface(mock_session)

    # Act
    result = await repository.get_all_like_code_or_name("", 1)

    # Assert
    mock_session.execute.assert_called_once()
    assert len(result) == 1
    assert result[0].drug_name == "TestDrug"
    assert result[0].drug_code == "TD123"
