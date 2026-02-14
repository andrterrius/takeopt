from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from tgbot.db.models import DBDistribution
from tgbot.db.repositories.base import SQLAlchemyRepository



class DistributionRepository(SQLAlchemyRepository[DBDistribution]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBDistribution)

    async def get(self, distribution_id: int) -> DBDistribution | None:
        return await self.get_by_id(distribution_id)

    async def get_by_uuid(self, distribution_uuid: UUID):
        query = select(self.model).where(self.model.uuid == distribution_uuid)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_count_distributions(self) -> int:
        return await self.get_count()

    async def save_distribution(self, distribution_instance: DBDistribution) -> DBDistribution:
        result_instance = await self.create(distribution_instance)
        return result_instance

    async def get_uui_by_id(self, distribution_id: int):
        query = select(DBDistribution.uuid).where(DBDistribution.id == distribution_id)
        result = await self._session.execute(query)
        uuid_value = result.scalar_one_or_none()
        return uuid_value