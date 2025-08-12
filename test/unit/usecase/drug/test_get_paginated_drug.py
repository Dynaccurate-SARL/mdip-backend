import pytest
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.drug.get_paginated import GetPaginatedDrugsUseCase
from src.application.dto.drug_dto import DrugPaginatedDto
from src.domain.entities.drug import Drug
from src.utils.exc import ResourceNotFound


@pytest.mark.asyncio
async def test_execute_returns_paginated_drug_dto():
    # Arrange
    mock_drug_catalog_repository = AsyncMock()
    mock_drug_catalog_repository.get_central.return_value = Mock(_id=123)

    mock_drug_repository = AsyncMock()
    mock_drug_repository.get_paginated_by_catalog_id.return_value = AsyncMock(
        items=[
            Drug._mock(1), Drug._mock(2),
        ],
        current_page=1,
        page_size=2,
        total_count=10
    )
    use_case = GetPaginatedDrugsUseCase(
        mock_drug_catalog_repository, mock_drug_repository)

    # Act
    result = await use_case.execute(
        page=1, page_size=2, name_or_code_filter="Drug")

    # Assert
    assert isinstance(result, DrugPaginatedDto)
    assert len(result.data) == 2
    assert result.page == 1
    assert result.limit == 2
    assert result.total == 10
    assert result.data[0].drug_name == "Drug 1"
    assert result.data[1].drug_code == "A2"
    mock_drug_repository.get_paginated_by_catalog_id.assert_awaited_once_with(
        1, 2, 123, "Drug"
    )

@pytest.mark.asyncio
async def test_execute_returns_paginated_drug_dto_invalid_catalog_id():
    # Arrange
    mock_drug_catalog_repository = AsyncMock()
    mock_drug_catalog_repository.get_by_id.return_value = None

    mock_drug_repository = AsyncMock()

    use_case = GetPaginatedDrugsUseCase(
        mock_drug_catalog_repository, mock_drug_repository)

    # Act
    with pytest.raises(ResourceNotFound) as exc_info:
        result = await use_case.execute(
            page=1, page_size=2, name_or_code_filter="Drug", catalog_id=1)
    
    #Assert
    assert exc_info.value.message == "Catalog not found"
