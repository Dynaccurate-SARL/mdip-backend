from src.utils.exc import UnauthorizedAccessError
from src.application.dto.auth_dto import AuthDto, AuthSuccessDto
from src.infrastructure.repositories.contract import UserRepositoryInterface
from src.infrastructure.services.token_service import TokenServiceInterface


class UserLoginUseCase:
    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 access_token_service: TokenServiceInterface,
                 refresh_token_service: TokenServiceInterface):
        self.user_repository = user_repository
        self.access_token_service = access_token_service
        self.refresh_token_service = refresh_token_service

    async def execute(self, credentials: AuthDto) -> AuthSuccessDto:
        user = await self.user_repository.get_user_by_email(
            credentials.username)
        if not user or not user.verify_password(credentials.password):
            raise UnauthorizedAccessError("Invalid credentials")

        access_token = self.access_token_service.generate_token(user.sub, [])
        refresh_token = self.refresh_token_service.generate_token(user.sub)

        return AuthSuccessDto(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='Bearer')
