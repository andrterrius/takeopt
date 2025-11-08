from typing import Optional
from tgbot.misc.logger import logger
from aiogram.utils.i18n import gettext as _


from tgbot.core.distribution.interfaces import ProcessingStatus, ICacheService, IThrottlingService, ILimitService, IChoiceProcessor
from tgbot.core.distribution.exceptions import ThrottlingChoiceException, CancelChoiceException
from tgbot.db.repositories.repository import Repository

class ChoiceProcessor(IChoiceProcessor):
    """Основной класс для обработки выбора пользователя
    """

    def __init__(self,
                 user_id: int,
                 distribution_id: int,
                 choiced_index: int,
                 cache_service: ICacheService,
                 repo: Repository,
                 throttling_service: IThrottlingService,
                 limit_service: ILimitService):

        self._user_id = user_id
        self._distribution_id = distribution_id
        self._choiced_index = choiced_index
        self._cache = cache_service
        self._repo = repo
        self._throttling = throttling_service
        self._limit_service = limit_service

        self._max_choices = None
        self._user_current_choices = None
        self._is_ready_deletion = False

        self._user_key = f"distribution:user:{distribution_id}:{user_id}"
        self._choice_key = f"distribution:choice:{distribution_id}:{choiced_index}"
        self._user_lock_key = f"user_lock:{distribution_id}:{user_id}"
        self._user_recent_choice_key = f"user_recent_choice:{distribution_id}:{user_id}"

    async def start_processing(self) -> ProcessingStatus:
        """
        Запуск полного пайплайна обработки выбора пользователя
        """
        try:

            await self._throttling.throttle_requests(self._user_lock_key)

            reservation = await self._throttling.reserve_choice(self._choice_key, self._user_key)
            if not reservation:
                raise ThrottlingChoiceException(_("Этот вариант обрабатывается, попробуй еще через несколько секунд!"))

            if await self._recent_request_for_cancel():
                await self._cancel_user_choice()

                return ProcessingStatus.CANCELED

            self._is_ready_deletion = await self._update_recent_cache()
            self._max_choices = await self._limit_service.get_max_choices(self._distribution_id)
            self._user_current_choices = await self._get_user_choices()

            self._limit_service.check_choice_limit(self._user_current_choices, self._max_choices)
            await self._save_user_choice()

            return ProcessingStatus.CHOICED

        except Exception as e:
            await self._repo.choices.rollback()

            await self._throttling.unreserve_choice(self._choice_key)

            process_ready_deletion = await self._exception_processing_ready_deletion()
            if process_ready_deletion:
                return process_ready_deletion
            raise

    async def update_user_choices(self) -> None:
        """Обновление количества выборов пользователя в кэше"""
        await self._cache.set(self._user_key, str(self._user_current_choices + 1), ex=300)

    async def _exception_processing_ready_deletion(self) -> Optional[ProcessingStatus]:
        """Обработка исключений при готовности к удалению"""
        if self._is_ready_deletion:
            user_choice = await self._check_user_choice()

            await self._throttling.unthrottle_requests(self._user_lock_key)

            if user_choice:
                return ProcessingStatus.PREPARED
            else:
                await self._remove_recent_cache()
        return None

    async def _update_recent_cache(self) -> bool:
        """Обновление кэша последнего выбора"""
        return await self._cache.set(self._user_recent_choice_key, str(self._choiced_index), ex=5)

    async def _remove_recent_cache(self) -> None:
        """Удаление кэша последнего выбора"""
        await self._cache.delete(self._user_recent_choice_key)

    async def _check_user_choice(self):
        """Проверка выбора пользователя в базе данных - используем существующий репозиторий"""
        response = await self._repo.choices.get_user_choice(
            self._distribution_id, self._choiced_index, self._user_id
        )
        return response

    async def _save_user_choice(self) -> None:
        """Сохранение выбора пользователя - используем существующий репозиторий"""
        await self._repo.choices.save_choice(
            distribution_id=self._distribution_id,
            button_index=self._choiced_index,
            user_id=self._user_id
        )

    async def _cancel_user_choice(self) -> bool:
        """Отмена выбора пользователя"""
        result = await self._repo.choices.cancel_choice(
            distribution_id=self._distribution_id,
            button_index=self._choiced_index,
            user_id=self._user_id
        )

        if result:
            await self._cleanup_user_cache()
        else:
            raise CancelChoiceException(_("Подожди, не так быстро, обрабатывается твой предыдущий запрос..."))
        return result

    async def _recent_request_for_cancel(self) -> bool:
        """Обработка повторного нажатия для отмены выбора"""
        recent_choice = await self._cache.get(self._user_recent_choice_key)
        return recent_choice == str(self._choiced_index)

    async def _get_user_choices(self) -> int:
        """Получение количества текущих выборов"""
        cached_choices = await self._cache.get(self._user_key)
        if cached_choices:
            return int(cached_choices)

        return await self._repo.choices.get_count_user_distribution_choices(
            self._distribution_id, self._user_id
        )

    async def _cleanup_user_cache(self) -> None:
        """Очистка кэша пользователя"""
        await self._cache.delete(self._user_key)
        await self._cache.delete(self._user_lock_key)