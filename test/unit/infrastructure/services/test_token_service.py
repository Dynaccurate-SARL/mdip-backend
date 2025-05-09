import jwt
import pytest
from datetime import datetime, timedelta, timezone

from src.infrastructure.services.token_service import IAccessTokenService, IRefreshTokenService, TokenPayload


@pytest.fixture
def access_token_service():
    secret_key = "test_secret_key"
    return IAccessTokenService(secret_key=secret_key, expiration=3600)


def test_generate_token(access_token_service):
    # Arrange
    sub = 1
    scopes = ["read", "write"]
    extra = {"key": "value"}

    # Act
    token = access_token_service.generate_token(
        sub=sub, scopes=scopes, extra=extra)

    # Assert
    assert isinstance(token, str)
    assert len(token) > 0


def test_get_token_payload(access_token_service):
    # Arrange
    sub = 1
    scopes = ["read", "write"]
    extra = {"key": "value"}
    token = access_token_service.generate_token(
        sub=sub, scopes=scopes, extra=extra)

    # Act
    payload = access_token_service.get_token_payload(token=token)

    # Assert
    assert isinstance(payload, TokenPayload)
    assert payload.sub == sub
    assert payload.scopes == scopes
    assert payload.extra == extra


def test_generate_token_with_default_expiration(access_token_service):
    # Arrange
    sub = 1
    scopes = ["read"]

    # Act
    token = access_token_service.generate_token(sub=sub, scopes=scopes)
    payload = access_token_service.get_token_payload(token=token)

    # Assert
    assert isinstance(payload, TokenPayload)
    assert payload.sub == sub
    assert payload.scopes == scopes
    assert payload.extra is None
    assert "exp" in jwt.decode(token, access_token_service._secret_key, algorithms=[
                               access_token_service._algorithm])

@pytest.mark.freeze_time('2025-04-30')
def test_generate_token_with_custom_expiration(access_token_service):
    # Arrange
    sub = 1
    scopes = ["read"]
    custom_expiration = datetime.now(timezone.utc) + timedelta(seconds=600)

    # Act
    token = access_token_service.generate_token(
        sub=sub, scopes=scopes, expiration=custom_expiration)
    payload = access_token_service.get_token_payload(token=token)

    # Assert
    assert isinstance(payload, TokenPayload)
    assert payload.sub == sub
    assert payload.scopes == scopes
    assert payload.extra is None

    decoded_token = jwt.decode(
        token, access_token_service._secret_key, algorithms=[
            access_token_service._algorithm]
    )
    assert "exp" in decoded_token
    assert datetime.fromtimestamp(
        decoded_token["exp"], tz=timezone.utc) == custom_expiration


@pytest.fixture
def refresh_token_service():
    secret_key = "test_refresh_secret_key"
    return IRefreshTokenService(secret_key=secret_key, expiration=7200)


def test_generate_refresh_token(refresh_token_service):
    # Arrange
    sub = "user_123"

    # Act
    token = refresh_token_service.generate_token(sub=sub)

    # Assert
    assert isinstance(token, str)
    assert len(token) > 0


def test_get_refresh_token_payload(refresh_token_service):
    # Arrange
    sub = 1
    token = refresh_token_service.generate_token(sub=sub)

    # Act
    payload = refresh_token_service.get_token_payload(token=token)

    # Assert
    assert isinstance(payload, TokenPayload)
    assert payload.sub == sub
    assert payload.scopes == []
    assert payload.extra is None

@pytest.mark.freeze_time('2025-04-30')
def test_generate_refresh_token_with_custom_expiration(refresh_token_service):
    # Arrange
    sub = 1
    custom_expiration = datetime.now(timezone.utc) + timedelta(seconds=1800)

    # Act
    token = refresh_token_service.generate_token(
        sub=sub, expiration=custom_expiration)
    payload = refresh_token_service.get_token_payload(token=token)

    # Assert
    assert isinstance(payload, TokenPayload)
    assert payload.sub == sub
    assert payload.scopes == []
    assert payload.extra is None
    
    decoded_token = jwt.decode(
        token, refresh_token_service._secret_key, algorithms=[
            refresh_token_service._algorithm]
    )
    assert "exp" in decoded_token
    assert datetime.fromtimestamp(
        decoded_token["exp"], tz=timezone.utc) == custom_expiration
