import pytest
from unittest.mock import AsyncMock
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.user import User
from src.infrastructure.repositories.iuser_repository import IUserRepository

password = "password123"
user = User(email="test@example.com", name="Test User", password=password)

def test_verify_password():
    # Assert
    assert user.verify_password(password) is True
    assert user.verify_password("wrong_password") is False
    

@pytest.mark.asyncio
async def test_save():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    repository = IUserRepository(mock_session)

    # Act
    result = await repository.save(user)

    # Assert
    mock_session.add.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(user)
    assert result == user


@pytest.mark.asyncio
async def test_get_by_sub():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalar_one_or_none.return_value = user

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IUserRepository(mock_session)

    # Act
    result = await repository.get_by_sub(1)

    # Assert
    mock_session.execute.assert_called_once()
    assert result == user


@pytest.mark.asyncio
async def test_get_user_by_email():
    # Arrange
    mock_execute_result = AsyncMock(spec=Result)
    mock_execute_result.scalar_one_or_none.return_value = user

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = mock_execute_result

    repository = IUserRepository(mock_session)

    # Act
    result = await repository.get_user_by_email("test@example.com")

    # Assert
    mock_session.execute.assert_called_once()
    assert result == user
