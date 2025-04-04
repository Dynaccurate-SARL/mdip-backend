from pydantic import EmailStr

from src.application.dto import BaseSchema


class UserCreateDto(BaseSchema):
    name: str
    email: EmailStr
    password: str

class UserResponseDto(BaseSchema):
    name: str
    email: EmailStr
