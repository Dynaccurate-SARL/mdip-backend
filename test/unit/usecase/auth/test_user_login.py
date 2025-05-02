import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.auth.user_login import UserLoginUseCase
from src.utils.exc import UnauthorizedAccessError
from src.application.dto.auth_dto import AuthDto, AuthSuccessDto


@pytest.mark.asyncio
async def test_user_login_success():
    # Arrange
    mock_user_repository = AsyncMock()
    mock_access_token_service = MagicMock()
    mock_refresh_token_service = MagicMock()

    mock_user = MagicMock()
    mock_user.sub = "user_id"
    mock_user.verify_password.return_value = True

    mock_user_repository.get_user_by_email.return_value = mock_user
    mock_access_token_service.generate_token.return_value = "access_token"
    mock_refresh_token_service.generate_token.return_value = "refresh_token"

    use_case = UserLoginUseCase(
        user_repository=mock_user_repository,
        access_token_service=mock_access_token_service,
        refresh_token_service=mock_refresh_token_service,
    )

    credentials = AuthDto(username="test@example.com", password="password")

    # Act
    result = await use_case.execute(credentials)

    # Assert
    assert isinstance(result, AuthSuccessDto)
    assert result.access_token == "access_token"
    assert result.refresh_token == "refresh_token"
    assert result.token_type == "Bearer"
    mock_user_repository.get_user_by_email.assert_awaited_once_with(
        "test@example.com")
    mock_access_token_service.generate_token.assert_called_once_with(
        "user_id", [])
    mock_refresh_token_service.generate_token.assert_called_once_with(
        "user_id")


@pytest.mark.asyncio
async def test_user_login_invalid_credentials():
    # Arrange
    mock_user_repository = AsyncMock()
    mock_access_token_service = MagicMock()
    mock_refresh_token_service = MagicMock()

    mock_user = MagicMock()
    mock_user.verify_password.return_value = False

    mock_user_repository.get_user_by_email.return_value = mock_user

    use_case = UserLoginUseCase(
        user_repository=mock_user_repository,
        access_token_service=mock_access_token_service,
        refresh_token_service=mock_refresh_token_service,
    )

    credentials = AuthDto(username="test@example.com",
                          password="wrong_password")

    # Act & Assert
    with pytest.raises(UnauthorizedAccessError, match="Invalid credentials"):
        await use_case.execute(credentials)

    mock_user_repository.get_user_by_email.assert_awaited_once_with(
        "test@example.com")


@pytest.mark.asyncio
async def test_user_login_user_not_found():
    # Arrange
    mock_user_repository = AsyncMock()
    mock_access_token_service = MagicMock()
    mock_refresh_token_service = MagicMock()

    mock_user_repository.get_user_by_email.return_value = None

    use_case = UserLoginUseCase(
        user_repository=mock_user_repository,
        access_token_service=mock_access_token_service,
        refresh_token_service=mock_refresh_token_service,
    )

    credentials = AuthDto(
        username="nonexistent@example.com", password="password")

    # Act & Assert
    with pytest.raises(UnauthorizedAccessError, match="Invalid credentials"):
        await use_case.execute(credentials)

    mock_user_repository.get_user_by_email.assert_awaited_once_with(
        "nonexistent@example.com")
