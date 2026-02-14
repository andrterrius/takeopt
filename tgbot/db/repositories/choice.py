from uuid import UUID

from sqlalchemy import asc, update, select, func, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.misc.logger import logger


from tgbot.db.models import DBChoice
from tgbot.db.repositories.base import SQLAlchemyRepository


class ChoiceRepository(SQLAlchemyRepository[DBChoice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBChoice)

    async def get(self, choice_id: int) -> DBChoice | None:
        return await self.get_by_id(choice_id)

    async def save_choice(self, distribution_id: int, button_index: int, user_id: int) -> DBChoice:
        new_choice = DBChoice(distribution_id=distribution_id, button_index=button_index, user_id=user_id)
        instance = await self.create(new_choice)
        return instance

    async def cancel_choice(self, distribution_id: int, button_index: int, user_id: int) -> int:
        updated_choice = update(DBChoice).where(
            self.model.distribution_id == distribution_id,
            self.model.button_index == button_index,
            self.model.user_id == user_id,
            self.model.active == True
        ).values(active=False)
        result = await self._session.execute(updated_choice)
        await self._session.flush()
        return result.rowcount

    async def get_all_choices_by_distribution_id(self, distribution_id: int) -> Sequence[DBChoice]:
        choices = await self.get_all(distribution_id=distribution_id, active=True, order_by=asc(self.model.button_index))
        return choices

    async def get_user_choices_by_distribution_id(self, distribution_id: int, user_id: int) -> Sequence[DBChoice]:
        choices = await self.get_all(distribution_id=distribution_id, user_id=user_id, active=True, order_by=asc(self.model.button_index))
        return choices

    async def get_all_choices_indexes(self, distribution_id: int) -> set[int]:
        choices = await self.get_all(distribution_id=distribution_id, active=True)
        return set(choice.button_index for choice in choices)

    async def get_count_user_distribution_choices(self, distribution_id, user_id) -> set[int]:
        select_req = select(func.count()).where(
            self.model.distribution_id == distribution_id,
            self.model.user_id == user_id,
            self.model.active == True
        )
        result = await self._session.execute(select_req)
        return result.scalar()

    async def get_user_choice(self, distribution_id: int, button_index: int, user_id: int) -> DBChoice | None:

        select_req = select(self.model).where(
            self.model.distribution_id == distribution_id,
            self.model.button_index == button_index,
            self.model.user_id == user_id,
            self.model.active == True
        )
        result = await self._session.execute(select_req)
        return result.scalar_one_or_none()

    async def rollback(self):
        return await self._session.rollback()