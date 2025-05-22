import bcrypt
import sqlalchemy as sq
from pydantic import EmailStr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.infrastructure.db.base import Base, generate_snowflake_id


class User(Base):
    __tablename__ = "users"

    sub: Mapped[int] = mapped_column(sq.BigInteger, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(sq.String(255), nullable=False)
    email: Mapped[str] = mapped_column(sq.String(255), unique=True, nullable=False)
    _password: Mapped[str] = mapped_column("password", sq.String, nullable=False)

    def __init__(self, name: str, email: EmailStr, password: str):
        self.name = name
        self.email = email
        self.password = password
        self.sub = generate_snowflake_id()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password: str):
        """Generates a hash from a plain-text password."""
        password_bytes = raw_password.encode("utf-8")
        password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self._password = password_hash.decode("utf-8")

    def verify_password(self, raw_password: str) -> bool:
        """Verifies a plain-text password against the stored hash."""
        return bcrypt.checkpw(
            raw_password.encode("utf-8"), self.password.encode("utf-8")
        )

    @staticmethod
    def _mock(sub: int = 1) -> "User":
        user = User(
            name=f"Test User {sub}",
            email=f"test.{sub}@example.com",
            password="hashed_password",
        )
        user.sub = sub
        return user
