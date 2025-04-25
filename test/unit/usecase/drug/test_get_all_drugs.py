import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.drug.get_all import GetAllDrugsByDrugNameOrCodeUseCase
from src.application.dto.drug_dto import DrugDto
from src.domain.entities.drug import Drug


@pytest.mark.asyncio
async def test_execute_returns_drug_dtos():
    # Arrange
    mock_drug_repository = AsyncMock()
    mock_drug_repository.get_all_like_code_or_name.return_value = [
        Drug._mock(1), Drug._mock(2)
    ]
    use_case = GetAllDrugsByDrugNameOrCodeUseCase(mock_drug_repository)
    drug_name_or_code = "Drug"

    # Act
    result = await use_case.execute(drug_name_or_code)

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], DrugDto)
    assert result[0].drug_name == "Drug 1"
    assert result[1].drug_code == "A2"
    mock_drug_repository.get_all_like_code_or_name.assert_awaited_once_with(
        drug_name_or_code)


@pytest.mark.asyncio
async def test_execute_returns_empty_list_when_no_drugs_found():
    # Arrange
    mock_drug_repository = AsyncMock()
    mock_drug_repository.get_all_like_code_or_name.return_value = []
    use_case = GetAllDrugsByDrugNameOrCodeUseCase(mock_drug_repository)
    drug_name_or_code = "NonExistentDrug"

    # Act
    result = await use_case.execute(drug_name_or_code)

    # Assert
    assert result == []
    mock_drug_repository.get_all_like_code_or_name.assert_awaited_once_with(
        drug_name_or_code)
