from src.utils.exc import UnauthorizedAccessError
from src.application.dto.auth_dto import AuthSuccessDto
from src.infrastructure.repositories.contract import UserRepositoryInterface
from src.infrastructure.services.token_service import TokenServiceInterface


class UserTokenRefreshUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        access_token_service: TokenServiceInterface,
        refresh_token_service: TokenServiceInterface,
    ):
        self.user_repository = user_repository
        self.access_token_service = access_token_service
        self.refresh_token_service = refresh_token_service

    async def execute(self, refresh_token: str) -> AuthSuccessDto:
        payload = self.refresh_token_service.get_token_payload(refresh_token)

        user = await self.user_repository.get_by_sub(payload.sub)
        if user is None:
            raise UnauthorizedAccessError("Invalid credentials")

        access_token = self.access_token_service.generate_token(user.sub, [])
        refresh_token = self.refresh_token_service.generate_token(user.sub)

        return AuthSuccessDto(
            access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
        )
