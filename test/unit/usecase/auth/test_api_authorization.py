import pytest
from jwt import InvalidTokenError
from fastapi.security import SecurityScopes
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.auth.api_authorization import ApiAuthorizationUseCase
from src.infrastructure.services.token_service import TokenPayload
from src.utils.exc import UnauthorizedAccessError
from src.domain.entities.user import User


@pytest.fixture
def mock_user_repository():
    return AsyncMock()


@pytest.fixture
def mock_token_service():
    return MagicMock()


@pytest.fixture
def use_case(mock_user_repository, mock_token_service):
    return ApiAuthorizationUseCase(
        user_repository=mock_user_repository,
        access_token_service=mock_token_service
    )


@pytest.mark.asyncio
async def test_execute_valid_token_and_permissions(use_case, mock_user_repository, mock_token_service):
    # Arrange
    token = "valid_token"
    security_scopes = SecurityScopes(scopes=["test"])
    token_payload = TokenPayload(sub=1, scopes=['test'])
    user = User._mock()

    mock_token_service.get_token_payload.return_value = token_payload
    mock_user_repository.get_by_sub.return_value = user

    # Act
    result = await use_case.execute(token, security_scopes)

    # Assert
    assert result == user
    mock_token_service.get_token_payload.assert_called_once_with(token)
    mock_user_repository.get_by_sub.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_execute_invalid_token(use_case, mock_token_service):
    # Arrange
    token = "invalid_token"
    security_scopes = SecurityScopes(scopes=["read"])

    mock_token_service.get_token_payload.side_effect = InvalidTokenError

    # Act & Assert
    with pytest.raises(UnauthorizedAccessError, match="Could not validate credentials"):
        await use_case.execute(token, security_scopes)


@pytest.mark.asyncio
async def test_execute_user_not_found(use_case, mock_user_repository, mock_token_service):
    # Arrange
    token = "valid_token"
    security_scopes = SecurityScopes(scopes=["test"])
    token_payload = TokenPayload(sub=1, scopes=['test'])

    mock_token_service.get_token_payload.return_value = token_payload
    mock_user_repository.get_by_sub.return_value = None

    # Act & Assert
    with pytest.raises(UnauthorizedAccessError, match="Could not validate credentials"):
        await use_case.execute(token, security_scopes)


@pytest.mark.asyncio
async def test_execute_insufficient_permissions(use_case, mock_user_repository, mock_token_service):
    # Arrange
    token = "valid_token"
    security_scopes = SecurityScopes(scopes=["test_admin"])
    token_payload = TokenPayload(sub=1, scopes=['test'])
    user = User._mock()

    mock_token_service.get_token_payload.return_value = token_payload
    mock_user_repository.get_by_sub.return_value = user

    # Act & Assert
    with pytest.raises(UnauthorizedAccessError, match="Not enough permissions"):
        await use_case.execute(token, security_scopes)
