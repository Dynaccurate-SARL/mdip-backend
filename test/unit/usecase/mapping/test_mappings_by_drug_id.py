import pytest
from unittest.mock import AsyncMock, MagicMock

from src.utils.exc import ResourceNotFound
from src.application.dto.mapping import CentralDrugMappingDto
from src.application.use_cases.mapping.mappings_by_drug_id import DrugMappingsUseCase


@pytest.mark.asyncio
async def test_execute_success():
    # Arrange
    drug_catalog_repository = AsyncMock()
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()

    central_catalog = MagicMock(id=1)
    central_drug = MagicMock(
        id='10', catalog_id=1, drug_name="Paracetamol", drug_code="PCT",
        properties={"dose": "500mg"}, country="XX")
    mapping1 = MagicMock(
        id='100', drug_name="Acetaminophen", drug_code="ACT",
        properties={"dose": "500mg"}, country="US"
    )
    mapping2 = MagicMock(
        id='101', drug_name="Paracetamol", drug_code="PCT",
        properties={"dose": "500mg"}, country="UK"
    )

    drug_catalog_repository.get_central.return_value = central_catalog
    drug_repository.get_by_id.return_value = central_drug
    mapping_repository.get_mappings_by_central_drug_id.return_value = [
        mapping1, mapping2]

    use_case = DrugMappingsUseCase(
        drug_catalog_repository=drug_catalog_repository,
        drug_repository=drug_repository,
        mapping_repository=mapping_repository
    )

    # Act
    result = await use_case.execute(10)

    # Assert
    assert isinstance(result, CentralDrugMappingDto)
    assert result.drug.id == '10'
    assert result.drug.drug_name == "Paracetamol"
    assert result.drug.drug_code == "PCT"
    assert result.drug.properties == {"dose": "500mg"}
    assert len(result.mappings) == 2
    assert result.mappings[0].drug_name == "Acetaminophen"
    assert result.mappings[1].country == "UK"


@pytest.mark.asyncio
async def test_execute_central_catalog_not_found():
    # Arrange
    drug_catalog_repository = AsyncMock()
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()

    drug_catalog_repository.get_central.return_value = None

    use_case = DrugMappingsUseCase(
        drug_catalog_repository=drug_catalog_repository,
        drug_repository=drug_repository,
        mapping_repository=mapping_repository
    )

    # Act & Assert
    with pytest.raises(ResourceNotFound):
        await use_case.execute(10)


@pytest.mark.asyncio
async def test_execute_central_drug_not_found():
    # Arrange
    drug_catalog_repository = AsyncMock()
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()

    central_catalog = MagicMock(id=1)
    drug_catalog_repository.get_central.return_value = central_catalog

    drug_repository.get_by_id.return_value = None

    use_case = DrugMappingsUseCase(
        drug_catalog_repository=drug_catalog_repository,
        drug_repository=drug_repository,
        mapping_repository=mapping_repository
    )

    # Act & Assert
    with pytest.raises(ResourceNotFound):
        await use_case.execute(10)
