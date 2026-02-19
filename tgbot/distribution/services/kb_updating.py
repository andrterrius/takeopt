import asyncio

from cachetools import LRUCache

from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter
from tgbot.db.repositories.repository import Repository
from tgbot.misc import callback_factory

from tgbot.misc.logger import logger

class DistributionLockManager:
    """Класс с asyncio блокировщиками, чтобы предотвратить race condition
    """
    def __init__(self):
        self._locks = LRUCache(maxsize=100)
        self._creation_lock = asyncio.Lock()

    async def get_lock(self, distribution_id: int, retry_count: int) -> asyncio.Lock:
        async with self._creation_lock:
            if distribution_id not in self._locks:
                self._locks[distribution_id] = asyncio.Lock()

            if retry_count > 0:
                self._locks[distribution_id].release()

            return self._locks[distribution_id]


class DistributionKeyboardUpdater:
    """Класс обновления клавиатуры с
    """

    MAX_RETRIES = 3

    _lock_manager = DistributionLockManager()

    @classmethod
    async def update_distribution_keyboard(
            cls,
            call: CallbackQuery,
            repo: Repository,
            distribution_id: int,
            distribution_deeplink: str,
            choiced_index: int = None,
            text: str = None,
            retry_count: int = 0
    ):
        distribution_lock = await cls._lock_manager.get_lock(distribution_id, retry_count)

        logger.error(f"Пробуем обновлять {distribution_id} {choiced_index}")

        async with distribution_lock:
            try:
                info_distribution = await repo.distributions.get(distribution_id)

                current_choices = await repo.choices.get_all_choices_indexes(
                    distribution_id=distribution_id
                )

                keyboard = cls._build_keyboard(
                    distribution_id=distribution_id,
                    distribution_deeplink=distribution_deeplink,
                    choices=current_choices,
                    range_start=info_distribution.range_data.start,
                    range_end=info_distribution.range_data.end,
                    choiced_index=choiced_index
                )

                if text:
                    await call.bot.edit_message_text(
                        text=text,
                        reply_markup=keyboard.as_markup(),
                        inline_message_id=call.inline_message_id
                    )
                else:
                    await call.bot.edit_message_reply_markup(
                        reply_markup=keyboard.as_markup(),
                        inline_message_id=call.inline_message_id
                    )
                return True

            except TelegramRetryAfter as e:
                if retry_count >= cls.MAX_RETRIES:
                    logger.error(f"Превышено максимальное количество попыток обновления клавиатуры {distribution_id}")
                    return False
                logger.error(f"Ошибка обновления клавиатуры {distribution_id}: {e}."
                             f"\nОжидаем {e.retry_after} секунд"
                             f"\nПопытка {retry_count+1}")
                await asyncio.sleep(e.retry_after)

                return await cls.update_distribution_keyboard(call, repo, distribution_id, choiced_index, text, retry_count=retry_count+1)

            except Exception as e:
                logger.error(f"Ошибка обновления клавиатуры {distribution_id}: {e}")
                return False

    @staticmethod
    def _build_keyboard(
            distribution_id: int,
            distribution_deeplink: str,
            choices: set[int],
            range_start: int,
            range_end: int,
            choiced_index: int | None = None
    ) -> InlineKeyboardBuilder:
        """Генерируем клавиатуру"""
        builder = InlineKeyboardBuilder()

        display_choices = choices | ({choiced_index} if choiced_index else set())

        auxiliary_buttons = [
            InlineKeyboardButton(text="❓", callback_data=callback_factory.GetHelp().pack()),
            InlineKeyboardButton(text="📄", url=distribution_deeplink),
            InlineKeyboardButton(text="👤", callback_data=callback_factory.GetMyDistributionChoices(
                distribution_id=distribution_id).pack())
        ]



        builder.row(*auxiliary_buttons)

        #range_end хранится в базе включительно, поэтому делаем +1
        for choice_index in range(range_start, range_end+1):
            is_taken = choice_index in display_choices
            emoji = "🔴" if is_taken else "🟢"

            builder.button(
                text=f"{choice_index} {emoji}",
                callback_data=callback_factory.MakeChoice(
                    distribution_id=distribution_id,
                    choiced_index=choice_index
                )
            )

        builder.adjust(len(auxiliary_buttons), 5)
        return builder