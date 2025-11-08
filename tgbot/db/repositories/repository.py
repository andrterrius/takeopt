from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.repositories.user import UserRepository
from tgbot.db.repositories.choice import ChoiceRepository
from tgbot.db.repositories.distribution import DistributionRepository


class Repository:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)
        self.distributions = DistributionRepository(session)
        self.choices = ChoiceRepository(session)
