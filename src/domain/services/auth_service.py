from typing import Annotated
from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from src.config.constants import C
from src.config.settings import get_config
from src.infrastructure.db.engine import get_session
from src.infrastructure.services.token_service import IAccessTokenService
from src.infrastructure.repositories.iuser_repository import IUserRepository
from src.application.use_cases.auth.api_authorization import ApiAuthorizationUseCase
from src.utils.exc import UnauthorizedAccessError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{C.URL_PREFIX}/docs/jwt")


async def manager(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    # Dependencies
    user_repository = IUserRepository(session)
    access_token_service = IAccessTokenService(get_config().JWT_SECRET)
    try:
        api_auth = ApiAuthorizationUseCase(user_repository, access_token_service)
        return await api_auth.execute(token, security_scopes)
    except UnauthorizedAccessError as e:
        return e.as_http_exception(status_code=status.HTTP_401_UNAUTHORIZED)
