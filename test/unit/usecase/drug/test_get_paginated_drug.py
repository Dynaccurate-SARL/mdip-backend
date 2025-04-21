import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.drug.get_paginated_drug import GetPaginatedDrugUseCase
from src.application.dto.drug_dto import DrugDto, DrugPaginatedDto
from src.domain.entities.drug import Drug


@pytest.mark.asyncio
async def test_execute_returns_paginated_drug_dto():
    # Arrange
    mock_repository = AsyncMock()
    mock_repository.get_paginated_by_catalog_id.return_value = AsyncMock(
        items=[
            Drug._mock(1), Drug._mock(2),
        ],
        current_page=1,
        page_size=2,
        total_count=10
    )
    use_case = GetPaginatedDrugUseCase(drug_repository=mock_repository)

    # Act
    result = await use_case.execute(
        page=1,
        page_size=2,
        catalog_id=123,
        name_or_code_filter="Drug"
    )

    # Assert
    assert isinstance(result, DrugPaginatedDto)
    assert len(result.data) == 2
    assert result.page == 1
    assert result.limit == 2
    assert result.total == 10
    assert result.data[0].drug_name == "Drug 1"
    assert result.data[1].drug_code == "A2"
    mock_repository.get_paginated_by_catalog_id.assert_awaited_once_with(
        1, 2, 123, "Drug"
    )
