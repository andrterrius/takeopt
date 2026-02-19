from tgbot.distribution.interfaces import IThrottlingService, ICacheService
from tgbot.distribution.exceptions import ThrottlingChoiceException

from aiogram.utils.i18n import gettext as _



class ThrottlingService(IThrottlingService):
    """Сервис контроля частоты запросов"""

    THROTTLING_TIME_SECONDS = 1
    CACHE_RESERVATION_TIME_SECONDS = 2


    def __init__(self, cache_service: ICacheService):
        self._cache = cache_service

    async def throttle_requests(self, user_lock_key: str) -> None:
        user_lock_acquired = await self._cache.set_nx(user_lock_key, "1", ex=self.THROTTLING_TIME_SECONDS)
        if not user_lock_acquired:
            raise ThrottlingChoiceException(_("Подожди, не так быстро, обрабатывается твой предыдущий запрос..."))

    async def unthrottle_requests(self, user_lock_key: str) -> None:
        await self._cache.delete(user_lock_key)

    async def reserve_choice(self, choice_key: str, user_key: str) -> bool:
        return await self._cache.set_nx(choice_key, user_key, ex=self.CACHE_RESERVATION_TIME_SECONDS)

    async def unreserve_choice(self, choice_key: str) -> None:
        await self._cache.delete(choice_key)