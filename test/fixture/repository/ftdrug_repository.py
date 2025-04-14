import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug import Drug
from src.infrastructure.repositories.contract import (
    DrugRepositoryInterface, PagedItems)


class MockDrugRepository(DrugRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._drug_obj1 = Drug(drug_name="Test Drug", drug_code="TD123",
                               catalog_id=1, properties={"hello": "world"})
        self._drug_obj1._id = 1

    async def save(self, drug: Drug) -> Drug:
        return drug

    async def get_by_id(self, id: int) -> Drug | None:
        return self._drug_obj1

    async def get_all_like_code_or_name(
            self, name_or_code: str) -> list[Drug]:
        return [self._drug_obj1]

    async def get_total_count(self, drug_catalog_id: int,
                              name_or_code_filter: str = None) -> int:
        return 10

    async def get_paginated_by_catalog_id(
        self, page: int, page_size: int, drug_catalog_id: int,
        name_or_code_filter: str = None
    ) -> PagedItems[Drug]:
        return PagedItems(
            items=[self._drug_obj1],
            total_count=10,
            current_page=page,
            page_size=page_size,
        )


@pytest.fixture
def mock_drug_repository(mock_session):
    # Arrange
    return MockDrugRepository(mock_session)
