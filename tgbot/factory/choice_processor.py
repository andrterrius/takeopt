from redis.asyncio import Redis
from tgbot.db.repositories.repository import Repository
from tgbot.distribution.choice_processor import ChoiceProcessor
from tgbot.distribution.services import RedisCacheService
from tgbot.distribution.services import ThrottlingService
from tgbot.distribution.services import LimitService


class ChoiceProcessorFactory:
    """Фабрика создания обработчика выборов"""

    @staticmethod
    def create(user_id: int, distribution_id: int, choiced_index: int,
               redis: Redis, repo: Repository):
        cache_service = RedisCacheService(redis)
        throttling_service = ThrottlingService(cache_service)
        limit_service = LimitService(cache_service, repo)  # Передаем repo напрямую

        return ChoiceProcessor(
            user_id=user_id,
            distribution_id=distribution_id,
            choiced_index=choiced_index,
            cache_service=cache_service,
            repo=repo,  # Передаем repo напрямую
            throttling_service=throttling_service,
            limit_service=limit_service
        )