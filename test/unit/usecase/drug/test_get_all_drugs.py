import pytest
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.drug.get_all import GetDrugsUseCase
from src.domain.entities.drug_mapping_count_view import DrugMappingCountView


@pytest.mark.asyncio
async def test_execute_returns_drug_dtos():
    # Arrange

    mock_drug_mapping_count_repository = AsyncMock()
    mock_drug_mapping_count_repository.get_all_like_code_or_name.return_value = [
        Mock(drug_code="A1", drug_name="Drug 1", spec=DrugMappingCountView),
        Mock(drug_code="A2", drug_name="Drug 2", spec=DrugMappingCountView)
    ]
    use_case = GetDrugsUseCase(mock_drug_mapping_count_repository)
    drug_name_or_code = "Drug"

    # Act
    result = await use_case.execute(drug_name_or_code, 0)

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], DrugMappingCountView)
    assert result[0].drug_name == "Drug 1"
    assert result[1].drug_code == "A2"
    mock_drug_mapping_count_repository.get_all_like_code_or_name.\
        assert_awaited_once_with(drug_name_or_code, 0)


@pytest.mark.asyncio
async def test_execute_returns_empty_list_when_no_drugs_found():
    # Arrange
    mock_drug_mapping_count_repository = AsyncMock()
    mock_drug_mapping_count_repository.get_all_like_code_or_name.return_value = []

    use_case = GetDrugsUseCase(mock_drug_mapping_count_repository)
    drug_name_or_code = "NonExistentDrug"

    # Act
    result = await use_case.execute(drug_name_or_code, 5)

    # Assert
    assert result == []
    mock_drug_mapping_count_repository.get_all_like_code_or_name.\
        assert_awaited_once_with(drug_name_or_code, 5)
