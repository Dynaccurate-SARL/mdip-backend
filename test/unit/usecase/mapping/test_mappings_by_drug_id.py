import pytest
from unittest.mock import AsyncMock, MagicMock
from src.application.use_cases.mapping.mappings_by_drug_id import DrugMappingsUseCase
from src.utils.exc import ResourceNotFound
from src.application.dto.mapping import CentralDrugMappingDto, MappingDrugDto, BaseDrugDto


@pytest.mark.asyncio
async def test_execute_success():
    # Arrange
    drug_catalog_repository = AsyncMock()
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()

    central_catalog = MagicMock(id="1")
    central_drug = MagicMock(id="10", catalog_id="1", drug_name="Drug A",
                             drug_code="A123", properties={"key": "value"})
    mappings = [
        MagicMock(id=20, drug_name="Drug B", drug_code="B123",
                  properties={"key": "value"}, country="EU"),
        MagicMock(id=21, drug_name="Drug C", drug_code="C123",
                  properties={"key": "value"}, country="EU"),
    ]

    drug_catalog_repository.get_central.return_value = central_catalog
    drug_repository.get_by_id.return_value = central_drug
    mapping_repository.get_mappings_by_central_drug_id.return_value = mappings

    use_case = DrugMappingsUseCase(
        drug_catalog_repository, drug_repository, mapping_repository)

    # Act
    result = await use_case.execute(drug_id=10)

    # Assert
    assert isinstance(result, CentralDrugMappingDto)
    assert result.drug == BaseDrugDto(
        id="10", drug_name="Drug A", drug_code="A123",
        properties={"key": "value"}
    )
    assert len(result.mappings) == 2
    assert result.mappings[0] == MappingDrugDto(
        id="20", drug_name="Drug B", drug_code="B123",
        properties={"key": "value"}, country="EU"
    )
    assert result.mappings[1] == MappingDrugDto(
        id="21", drug_name="Drug C", drug_code="C123",
        properties={"key": "value"}, country="EU"
    )


@pytest.mark.asyncio
async def test_execute_central_catalog_not_found():
    # Arrange
    drug_catalog_repository = AsyncMock()
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()

    drug_catalog_repository.get_central.return_value = None

    use_case = DrugMappingsUseCase(
        drug_catalog_repository, drug_repository, mapping_repository)

    # Act & Assert
    with pytest.raises(ResourceNotFound,
                       match="Central catalog does not exist"):
        await use_case.execute(drug_id=10)


@pytest.mark.asyncio
async def test_execute_drug_not_found_in_central_catalog():
    # Arrange
    drug_catalog_repository = AsyncMock()
    drug_repository = AsyncMock()
    mapping_repository = AsyncMock()

    central_catalog = MagicMock(id=1)
    drug_catalog_repository.get_central.return_value = central_catalog
    drug_repository.get_by_id.return_value = None

    use_case = DrugMappingsUseCase(
        drug_catalog_repository, drug_repository, mapping_repository)

    # Act & Assert
    with pytest.raises(ResourceNotFound,
                       match="Drug not found in central catalog"):
        await use_case.execute(drug_id=10)
