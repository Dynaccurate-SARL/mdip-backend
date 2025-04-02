from pydantic import EmailStr
from src.application.dto import BaseSchema


class LoginDto(BaseSchema):
    username: EmailStr
    password: str

class LoginResponseDto(BaseSchema):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None