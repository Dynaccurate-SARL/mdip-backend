import logging
from jwt import InvalidTokenError
from pydantic import ValidationError
from fastapi import HTTPException, status
from fastapi.security import SecurityScopes

from src.domain.entities.user import User
from src.infrastructure.repositories.contract import UserRepositoryInterface
from src.infrastructure.services.token_service import TokenServiceInterface


class ApiAuthorizationUseCase:
    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 access_token_service: TokenServiceInterface):
        self.user_repository = user_repository
        self.access_token_service = access_token_service

    async def execute(
            self, token: str, security_scopes: SecurityScopes) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

        try:
            payload = self.access_token_service.get_token_payload(token)
        except (InvalidTokenError, ValidationError):
            raise credentials_exception

        user = await self.user_repository.get_user_by_sub(payload.sub)
        if user is None:
            raise credentials_exception

        authenticate_value = "Bearer"
        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'

        if security_scopes.scopes:
            intersection = list(
                set(payload["scopes"]) & set(security_scopes.scopes))
            if not intersection:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        logging.info(f'Access by: {user.name}')
        return user
