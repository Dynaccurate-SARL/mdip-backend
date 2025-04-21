import pytest

from unittest.mock import AsyncMock
from src.application.use_cases.drug.get_by_id import GetDrugByIdUseCase
from src.application.dto.drug_dto import DrugDto
from src.infrastructure.repositories.contract import DrugRepositoryInterface


@pytest.mark.asyncio
async def test_execute_returns_drug_dto():
    mock_repository = AsyncMock(spec=DrugRepositoryInterface)
    mock_drug = {"id": '1', 'catalog_id': '1', "drug_name": "Aspirin",
                 "drug_code": 'A1', "properties": {}}
    mock_repository.get_by_id.return_value = mock_drug

    use_case = GetDrugByIdUseCase(drug_repository=mock_repository)
    result = await use_case.execute(drug_id=1)

    assert result == DrugDto.model_validate(mock_drug)
    mock_repository.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_execute_returns_none_when_drug_not_found():
    mock_repository = AsyncMock(spec=DrugRepositoryInterface)
    mock_repository.get_by_id.return_value = None

    use_case = GetDrugByIdUseCase(drug_repository=mock_repository)
    result = await use_case.execute(drug_id=1)

    assert result is None
    mock_repository.get_by_id.assert_called_once_with(1)
