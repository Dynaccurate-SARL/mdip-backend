from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, Header, status

from src.config.settings import get_config
from src.utils.exc import UnauthorizedAccessError
from src.infrastructure.db.engine import get_session
from src.application.dto.auth_dto import AuthSuccessDto, AuthDto
from src.application.use_cases.auth.user_login import UserLoginUseCase
from src.infrastructure.repositories.iuser_repository import IUserRepository
from src.application.use_cases.auth.user_token_refresh import (
    UserTokenRefreshUseCase
)
from src.infrastructure.services.token_service import (
    IAccessTokenService, IRefreshTokenService
)


auth_router = APIRouter()


@auth_router.post('/docs/jwt', include_in_schema=False)
async def auth_token(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user_repository = IUserRepository(session)
    access_token_service = IAccessTokenService(get_config().JWT_SECRET)
    refresh_token_service = IRefreshTokenService(get_config().JWT_SECRET)

    try:
        login_use_case = UserLoginUseCase(
            user_repository, access_token_service, refresh_token_service)
        return await login_use_case.execute(
            AuthDto(username=data.username, password=data.password))
    except UnauthorizedAccessError as e:
        return e.as_response(status_code=status.HTTP_401_UNAUTHORIZED)


@auth_router.post('/login', response_model=AuthSuccessDto)
async def login(data: AuthDto,
                session: Annotated[AsyncSession, Depends(get_session)]):
    user_repository = IUserRepository(session)
    access_token_service = IAccessTokenService(get_config().JWT_SECRET)
    refresh_token_service = IRefreshTokenService(get_config().JWT_SECRET)

    try:
        login_use_case = UserLoginUseCase(
            user_repository, access_token_service, refresh_token_service)
        return await login_use_case.execute(
            AuthDto(username=data.username, password=data.password))
    except UnauthorizedAccessError as e:
        return e.as_response(status_code=status.HTTP_401_UNAUTHORIZED)


@auth_router.post('/refresh')
async def refresh(
    refresh_token: Annotated[str, Header(
        ..., description='Refresh Token', alias='x-refresh-token'
    )],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user_repository = IUserRepository(session)
    access_token_service = IAccessTokenService(get_config().JWT_SECRET)
    refresh_token_service = IRefreshTokenService(get_config().JWT_SECRET)

    try:
        refresh_token_use_case = UserTokenRefreshUseCase(
            user_repository, access_token_service, refresh_token_service)
        return await refresh_token_use_case.execute(refresh_token)
    except UnauthorizedAccessError as e:
        return e.as_response(status_code=status.HTTP_401_UNAUTHORIZED)
