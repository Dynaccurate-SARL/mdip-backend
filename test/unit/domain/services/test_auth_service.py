import pytest
from fastapi import HTTPException, status
from fastapi.security import SecurityScopes
from unittest.mock import AsyncMock, MagicMock

from src.utils.exc import UnauthorizedAccessError
from src.domain.services.auth_service import manager

@pytest.mark.asyncio
async def test_manager_success():
    # Arrange
    mock_token = "valid_token"
    mock_session = AsyncMock()
    mock_security_scopes = SecurityScopes(scopes=["read"])
    mock_user_repository = MagicMock()
    mock_access_token_service = MagicMock()
    mock_api_auth = AsyncMock()
    mock_api_auth.execute.return_value = "user_data"

    # Mock dependencies
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.domain.services.auth_service.IUserRepository", lambda _: mock_user_repository)
        mp.setattr("src.domain.services.auth_service.IAccessTokenService", lambda _: mock_access_token_service)
        mp.setattr("src.domain.services.auth_service.ApiAuthorizationUseCase", lambda *_: mock_api_auth)

        # Act
        result = await manager(mock_security_scopes, mock_token, mock_session)

    # Assert
    mock_api_auth.execute.assert_called_once_with(mock_token, mock_security_scopes)
    assert result == "user_data"

@pytest.mark.asyncio
async def test_manager_unauthorized_access_error():
    # Arrange
    mock_token = "invalid_token"
    mock_session = AsyncMock()
    mock_security_scopes = SecurityScopes(scopes=["read"])
    mock_user_repository = MagicMock()
    mock_access_token_service = MagicMock()
    mock_api_auth = AsyncMock()
    mock_api_auth.execute.side_effect = UnauthorizedAccessError("Unauthorized")

    # Mock dependencies
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.domain.services.auth_service.IUserRepository", lambda _: mock_user_repository)
        mp.setattr("src.domain.services.auth_service.IAccessTokenService", lambda _: mock_access_token_service)
        mp.setattr("src.domain.services.auth_service.ApiAuthorizationUseCase", lambda *_: mock_api_auth)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await manager(mock_security_scopes, mock_token, mock_session)
            
        assert exc_info.value.detail == "Unauthorized"
        mock_api_auth.execute.assert_called_once_with(mock_token, mock_security_scopes)
