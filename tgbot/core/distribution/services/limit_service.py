from tgbot.core.distribution.interfaces import ILimitService, ICacheService
from tgbot.core.distribution.exceptions import LimitChoiceException

from aiogram.utils.i18n import gettext as _


class LimitService(ILimitService):
    """Сервис проверки лимитов"""

    CACHE_CHOICE_LIMIT_TIME_SECONDS = 300

    def __init__(self, cache_service: ICacheService, repo):
        self._cache = cache_service
        self._repo = repo

    async def get_max_choices(self, distribution_id: int) -> int:
        max_choices_key = f"limit:distribution:{distribution_id}"
        max_choices = await self._cache.get(max_choices_key)

        if not max_choices:
            distribution_info = await self._repo.distributions.get(distribution_id)
            max_choices_value = distribution_info.count_choices
            await self._cache.set(max_choices_key, str(max_choices_value), ex=self.CACHE_CHOICE_LIMIT_TIME_SECONDS)
            return max_choices_value

        return int(max_choices)

    def check_choice_limit(self, user_current_choices: int, max_choices: int) -> None:
        if user_current_choices >= max_choices:
            raise LimitChoiceException(_("Ты уже выбрал допустимое количество вариантов!"))