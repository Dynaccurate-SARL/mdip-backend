from pydantic import EmailStr, Field

from src.application.dto import BaseSchema


class AuthDto(BaseSchema):
    username: EmailStr = Field(examples=["johndoe@example.com"])
    password: str = Field(examples=["mysecretpassword"])

class AuthSuccessDto(BaseSchema):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None