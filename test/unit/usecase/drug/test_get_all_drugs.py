import pytest
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.drug.get_all import GetAllDrugsUseCase
from src.application.dto.drug_dto import DrugDto
from src.domain.entities.drug import Drug


@pytest.mark.asyncio
async def test_execute_returns_drug_dtos():
    # Arrange
    mock_drug_catalog_repository = AsyncMock()
    mock_drug_catalog_repository.get_central.return_value = Mock(_id=1)
    mock_drug_repository = AsyncMock()
    mock_drug_repository.get_all_like_code_or_name_by_catalog_id.return_value = [
        Drug._mock(1), Drug._mock(2)
    ]
    use_case = GetAllDrugsUseCase(
        mock_drug_catalog_repository, mock_drug_repository)
    drug_name_or_code = "Drug"

    # Act
    result = await use_case.execute(drug_name_or_code)

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], DrugDto)
    assert result[0].drug_name == "Drug 1"
    assert result[1].drug_code == "A2"
    mock_drug_repository.get_all_like_code_or_name_by_catalog_id.\
        assert_awaited_once_with(1, drug_name_or_code)


@pytest.mark.asyncio
async def test_execute_returns_empty_list_when_no_drugs_found():
    # Arrange
    mock_drug_catalog_repository = AsyncMock()
    mock_drug_catalog_repository.get_central.return_value = Mock(_id=1)
    mock_drug_repository = AsyncMock()
    mock_drug_repository.get_all_like_code_or_name_by_catalog_id.return_value = []

    use_case = GetAllDrugsUseCase(
        mock_drug_catalog_repository, mock_drug_repository)
    drug_name_or_code = "NonExistentDrug"

    # Act
    result = await use_case.execute(drug_name_or_code)

    # Assert
    assert result == []
    mock_drug_repository.get_all_like_code_or_name_by_catalog_id.\
        assert_awaited_once_with(1, drug_name_or_code)
