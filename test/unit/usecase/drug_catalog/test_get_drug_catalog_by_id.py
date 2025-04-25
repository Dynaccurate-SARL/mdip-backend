import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.drug_catalog.get_by_id import GetDrugCatalogByIdUseCase
from src.application.dto.drug_catalog_dto import DrugCatalogDto
from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import DrugCatalogRepositoryInterface


@pytest.mark.asyncio
async def test_execute_returns_drug_catalog_dto():
    # Arrange
    mock_repository = AsyncMock(spec=DrugCatalogRepositoryInterface)
    drug_catalog_id = 1
    mock_repository.get_by_id.return_value = DrugCatalog._mock(
        number=drug_catalog_id)
    use_case = GetDrugCatalogByIdUseCase(mock_repository)

    # Act
    result = await use_case.execute(drug_catalog_id)

    # Assert
    assert result is not None
    assert isinstance(result, DrugCatalogDto)
    assert result.id == str(drug_catalog_id)
    assert result.name == "Drug Catalog 1"
    mock_repository.get_by_id.assert_awaited_once_with(drug_catalog_id)


@pytest.mark.asyncio
async def test_execute_returns_none_when_drug_catalog_not_found():
    # Arrange
    mock_repository = AsyncMock(spec=DrugCatalogRepositoryInterface)
    drug_catalog_id = 1
    mock_repository.get_by_id.return_value = None
    use_case = GetDrugCatalogByIdUseCase(mock_repository)

    # Act
    result = await use_case.execute(drug_catalog_id)

    # Assert
    assert result is None
    mock_repository.get_by_id.assert_awaited_once_with(drug_catalog_id)
