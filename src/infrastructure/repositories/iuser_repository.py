from pydantic import EmailStr
from sqlalchemy.future import select

from src.domain.entities.user import User
from src.infrastructure.repositories.contract import UserRepositoryInterface


class IUserRepository(UserRepositoryInterface):
    async def save(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_sub(self, sub: int):
        query = select(User).where(User.sub == sub)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_email(self, email: EmailStr):
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user
