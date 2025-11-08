from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models import DBDistribution
from tgbot.db.repositories.base import SQLAlchemyRepository


class DistributionRepository(SQLAlchemyRepository[DBDistribution]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBDistribution)

    async def get(self, distribution_id: int) -> DBDistribution | None:
        return await self.get_by_id(distribution_id)

    async def get_count_distributions(self) -> int:
        return await self.get_count()

    async def save_distribution(self, distribution_instance: DBDistribution) -> DBDistribution:
        result_instance = await self.create(distribution_instance)
        return result_instance
