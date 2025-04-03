import hashlib
import sqlalchemy as sq
from pydantic import EmailStr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.domain.entities import Base, generate_snowflake_id


class User(Base):
    __tablename__ = 'users'

    sub: Mapped[int] = mapped_column(
        sq.BigInteger, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(sq.String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        sq.String(255), unique=True, nullable=False)
    _password: Mapped[str] = mapped_column(
        "password", sq.String, nullable=False)

    def __init__(self, name: str, email: EmailStr, password: str):
        self.name = name
        self.email = email
        self.password = hashlib.sha256(
            password.encode('utf-8')).hexdigest()
        self.sub = generate_snowflake_id()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        hashed_password = hashlib.sha256(
            raw_password.encode('utf-8')).hexdigest()
        self._password = hashed_password

    def verify_password(self, raw_password: str) -> bool:
        hashed_password = hashlib.sha256(
            raw_password.encode('utf-8')).hexdigest()
        return hashed_password == self._password

    def _alembic_user(self):
        return {
            'sub': self.sub,
            'name': self.name,
            'email': self.email,
            'password': self.password
        }
