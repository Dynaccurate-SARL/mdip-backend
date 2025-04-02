from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from src.config.constants import C
from src.config.settings import get_config
from src.infrastructure.db.engine import get_session
from src.infrastructure.services.token_service import IAccessTokenService
from src.infrastructure.repositories.iuser_repository import UserRepository
from src.application.use_cases.auth.api_authorization import ApiAuthorizationUseCase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{C.API_PREFIX}/docs/jwt')


async def manager(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    # Dependencies
    user_repository = UserRepository(session)
    access_token_service = IAccessTokenService(get_config().JWT_SECRET)

    api_auth = ApiAuthorizationUseCase(user_repository, access_token_service)
    return await api_auth.execute(security_scopes, token)
