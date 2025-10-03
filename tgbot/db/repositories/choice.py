from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models import DBChoice
from tgbot.db.repositories.base import SQLAlchemyRepository


class ChoiceRepository(SQLAlchemyRepository[DBChoice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBChoice)

    async def get(self, choice_id: int) -> DBChoice | None:
        return await self.get_by_id(choice_id)

    async def save_choice(self, choice: DBChoice) -> DBChoice:
        instance = await self.create(choice)
        return instance

    async def get_all_choices_indexes(self, distribution_id) -> set[int]:
        choices = await self.get_all(distribution_id=distribution_id)
        return set(choice.button_index for choice in choices)