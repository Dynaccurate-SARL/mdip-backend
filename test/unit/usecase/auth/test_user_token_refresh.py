import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.auth.user_token_refresh import UserTokenRefreshUseCase
from src.utils.exc import UnauthorizedAccessError
from src.application.dto.auth_dto import AuthSuccessDto


@pytest.fixture
def mock_user_repository():
    return AsyncMock()


@pytest.fixture
def mock_access_token_service():
    return MagicMock()


@pytest.fixture
def mock_refresh_token_service():
    return MagicMock()


@pytest.fixture
def use_case(mock_user_repository, mock_access_token_service, mock_refresh_token_service):
    return UserTokenRefreshUseCase(
        user_repository=mock_user_repository,
        access_token_service=mock_access_token_service,
        refresh_token_service=mock_refresh_token_service
    )


@pytest.mark.asyncio
async def test_execute_success(
        use_case, mock_user_repository, mock_access_token_service,
        mock_refresh_token_service):
    # Arrange
    mock_refresh_token_service.get_token_payload.return_value = MagicMock(
        sub="user123")
    mock_user_repository.get_by_sub.return_value = MagicMock(sub="user123")
    mock_access_token_service.generate_token.return_value = "new_access_token"
    mock_refresh_token_service.generate_token.return_value = "new_refresh_token"

    # Act
    result = await use_case.execute("valid_refresh_token")

    # Assert
    assert isinstance(result, AuthSuccessDto)
    assert result.access_token == "new_access_token"
    assert result.refresh_token == "new_refresh_token"
    assert result.token_type == "Bearer"
    mock_refresh_token_service.get_token_payload.assert_called_once_with(
        "valid_refresh_token")
    mock_user_repository.get_by_sub.assert_called_once_with("user123")
    mock_access_token_service.generate_token.assert_called_once_with(
        "user123", [])
    mock_refresh_token_service.generate_token.assert_called_once_with(
        "user123")


@pytest.mark.asyncio
async def test_execute_invalid_user(
        use_case, mock_user_repository, mock_refresh_token_service):
    # Arrange
    mock_refresh_token_service.get_token_payload.return_value = MagicMock(
        sub="user123")
    mock_user_repository.get_by_sub.return_value = None

    # Act & Assert
    with pytest.raises(UnauthorizedAccessError, match="Invalid credentials"):
        await use_case.execute("valid_refresh_token")

    mock_refresh_token_service.get_token_payload.assert_called_once_with(
        "valid_refresh_token")
    mock_user_repository.get_by_sub.assert_called_once_with("user123")
