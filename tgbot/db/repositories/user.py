from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models import Base, DBUser
from tgbot.db.repositories.base import SQLAlchemyRepository

T = TypeVar("T", bound=Base)


class UserRepository(SQLAlchemyRepository[DBUser]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBUser)

    async def get(self, user_id: int) -> DBUser | None:
        return await self.get_by_id(user_id)

    async def get_count_users(self) -> int:
        return await self.get_count()

    async def save_user(self, user: DBUser) -> DBUser:
        instance = await self.create(user)
        await self._session.commit()
        return instance
