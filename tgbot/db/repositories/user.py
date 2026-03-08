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

    async def update_user(self, user: DBUser) -> DBUser:
        instance = await self.update(user)
        await self._session.commit()
        return instance

    async def get_or_update_user(self, user_id: int, name: str, username: str | None) -> DBUser:
        user = await self.get(user_id)

        if not user:
            new_user = DBUser(id=user_id, name=name, username=username)
            return await self.save_user(new_user)

        needs_update = False

        if user.name != name:
            user.name = name
            needs_update = True

        if user.username != username:
            user.username = username
            needs_update = True

        if needs_update:
            return await self.update_user(user)

        return user