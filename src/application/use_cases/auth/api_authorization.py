import logging
from jwt import InvalidTokenError
from pydantic import ValidationError
from fastapi.security import SecurityScopes

from src.domain.entities.user import User
from src.infrastructure.repositories.contract import UserRepositoryInterface
from src.infrastructure.services.token_service import TokenServiceInterface
from src.utils.exc import UnauthorizedAccessError


class ApiAuthorizationUseCase:
    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 access_token_service: TokenServiceInterface):
        self.user_repository = user_repository
        self.access_token_service = access_token_service

    async def execute(
            self, token: str, security_scopes: SecurityScopes) -> User:
        try:
            payload = self.access_token_service.get_token_payload(token)
        except (InvalidTokenError, ValidationError):
            raise UnauthorizedAccessError("Could not validate credentials")

        user = await self.user_repository.get_user_by_sub(payload.sub)
        if user is None:
            raise UnauthorizedAccessError("Could not validate credentials")

        if security_scopes.scopes:
            intersection = list(
                set(payload["scopes"]) & set(security_scopes.scopes))
            if not intersection:
                raise UnauthorizedAccessError("Not enough permissions")
        logging.info(f'Access by: {user.name}')
        return user
