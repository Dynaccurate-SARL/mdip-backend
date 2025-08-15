import pytest
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.drug.get_by_id import GetDrugByIdUseCase
from src.application.dto.drug_dto import DrugDto
from src.infrastructure.repositories.contract import (
    DrugRepositoryInterface, MappingRepositoryInterface)


@pytest.mark.asyncio
async def test_execute_returns_drug_dto():
    # Arrange
    mock_drug_repository = AsyncMock(spec=DrugRepositoryInterface)
    mock_mapping_repository = AsyncMock(spec=MappingRepositoryInterface)
    mock_drug = Mock(
        id='1', catalog_id='1', drug_name="Aspirin", drug_code='A1',
        properties={}, _id=1, country="XX", mapping_parents=[])
    mock_drug_repository.get_by_id.return_value = mock_drug
    mock_mapping_repository.get_drugs_id_by_related_to.return_value = []
    use_case = GetDrugByIdUseCase(
        drug_repository=mock_drug_repository,
        mapping_repository=mock_mapping_repository)

    # Act
    result = await use_case.execute(drug_id=1)

    # Assert
    assert result == DrugDto.model_validate(mock_drug)
    mock_drug_repository.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_execute_returns_none_when_drug_not_found():
    # Arrange
    mock_drug_repository = AsyncMock(spec=DrugRepositoryInterface)
    mock_mapping_repository = AsyncMock(spec=MappingRepositoryInterface)
    mock_drug_repository.get_by_id.return_value = None
    mock_mapping_repository.get_drugs_id_by_related_to.return_value = []
    use_case = GetDrugByIdUseCase(
        drug_repository=mock_drug_repository,
        mapping_repository=mock_mapping_repository)

    # Act
    result = await use_case.execute(drug_id=1)

    # Assert
    assert result is None
    mock_drug_repository.get_by_id.assert_called_once_with(1)
