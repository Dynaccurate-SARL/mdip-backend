import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.drug_catalog.get_paginated_drug_catalog import GetPaginatedDrugCatalogUseCase
from src.domain.entities.drug_catalog import DrugCatalog
from src.infrastructure.repositories.contract import DrugCatalogRepositoryInterface
from src.application.dto.drug_catalog_dto import DrugCatalogPaginatedDto


@pytest.mark.asyncio
async def test_get_paginated_drug_catalog_use_case():
    # Arrange
    mock_repository = AsyncMock(spec=DrugCatalogRepositoryInterface)
    mock_repository.get_paginated.return_value = AsyncMock(
        items=[
            DrugCatalog._mock(1),
            DrugCatalog._mock(2)
        ],
        current_page=1,
        page_size=2,
        total_count=10
    )
    use_case = GetPaginatedDrugCatalogUseCase(mock_repository)

    # Act
    result = await use_case.execute(page=1, page_size=2, name="Drug")

    # Assert
    assert isinstance(result, DrugCatalogPaginatedDto)
    assert len(result.data) == 2
    assert result.page == 1
    assert result.limit == 2
    assert result.total == 10
    assert result.data[0].name == "Drug Catalog 1"
    assert result.data[1].name == "Drug Catalog 2"
    mock_repository.get_paginated.assert_awaited_once_with(1, 2, "Drug")
