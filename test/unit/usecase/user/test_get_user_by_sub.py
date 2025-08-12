import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.user.get_by_sub import GetUserBySubUseCase
from src.application.dto.user_dto import UserDto
from src.domain.entities.user import User


@pytest.mark.asyncio
async def test_execute_with_valid_sub():
    # Arrange
    mock_user_repository = AsyncMock()
    mock_user_repository.get_by_sub.return_value = User._mock()
    use_case = GetUserBySubUseCase(mock_user_repository)

    # Act
    result = await use_case.execute(1)

    # Assert
    assert result is not None
    assert isinstance(result, UserDto)
    mock_user_repository.get_by_sub.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_execute_with_invalid_sub():
    # Arrange
    mock_user_repository = AsyncMock()
    mock_user_repository.get_by_sub.return_value = None
    use_case = GetUserBySubUseCase(mock_user_repository)

    # Act
    result = await use_case.execute(3)

    # Assert
    assert result is None
    mock_user_repository.get_by_sub.assert_awaited_once_with(3)


@pytest.mark.asyncio
async def test_execute_with_empty_sub():
    # Arrange
    mock_user_repository = AsyncMock()
    use_case = GetUserBySubUseCase(mock_user_repository)

    # Act & Assert
    with pytest.raises(ValueError, match="Sub cannot be empty"):
        await use_case.execute("")
