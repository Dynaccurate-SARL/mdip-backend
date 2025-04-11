from typing import Annotated
from fastapi import APIRouter, Depends

from src.domain.entities.user import User
from src.domain.services.auth_service import manager
from src.application.dto.user_dto import UserDto


user_router = APIRouter()


@user_router.get("/me", response_model=UserDto)
async def get_by_id(user: Annotated[User, Depends(manager)]):
    return UserDto.model_validate(user)
