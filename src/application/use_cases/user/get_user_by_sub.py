from src.application.dto.user_dto import UserResponseDto
from src.infrastructure.repositories.contract import UserRepositoryInterface


class GetUserBySubUseCase:
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(self, sub: str) -> UserResponseDto | None:
        if not sub:
            raise ValueError("Sub cannot be empty")
        user = await self.user_repository.get_user_by_sub(sub)
        if user:
            return UserResponseDto.model_validate(user)
