import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.user import User
from src.infrastructure.repositories.imapping_repository import IMappingRepository

user = User(email="test@example.com",
            name="Test User", password="password123")


@pytest.mark.asyncio
async def test_save():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    repository = IMappingRepository(mock_session)

    # Act
    result = await repository.save(user)

    # Assert
    mock_session.add.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(user)
    assert result == user

@pytest.mark.asyncio
async def test_get_mappings_by_central_drug_id():
    # Arrange
    central_drug_id = 1
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_result.fetchall.return_value = [
        MagicMock(
            id=1,
            drug_code="D001",
            drug_name="Drug A",
            country="US",
            properties={"key": "value"}
        ),
        MagicMock(
            id=2,
            drug_code="D002",
            drug_name="Drug B",
            country="CA",
            properties={"key": "value2"}
        )
    ]

    repository = IMappingRepository(mock_session)

    # Act
    result = await repository.get_mappings_by_central_drug_id(central_drug_id)

    # Assert
    mock_session.execute.assert_called_once()
    mock_result.fetchall.assert_called_once()
    assert len(result) == 2
    assert result[0].id == 1
    assert result[0].drug_code == "D001"
    assert result[0].drug_name == "Drug A"
    assert result[0].country == "US"
    assert result[0].properties == {"key": "value"}
    assert result[1].id == 2
    assert result[1].drug_code == "D002"
    assert result[1].drug_name == "Drug B"
    assert result[1].country == "CA"
    assert result[1].properties == {"key": "value2"}
