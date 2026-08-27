import asyncio
from collections.abc import Sequence

from cachetools import LRUCache

from aiogram.enums import ButtonStyle
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import (
    CallbackQuery,
    InputRichBlockButtons,
    InputRichBlockParagraph,
    InputRichMessage,
    RichMessageButton,
    RichTextCustomEmoji,
)
from tgbot.core.config import DistributionConfig
from tgbot.db.repositories.repository import Repository
from tgbot.misc import callback_factory

from tgbot.misc.logger import logger

DEFAULT_DISTRIBUTION_TEXT = "❓- основная информация"


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
    """Класс обновления rich-сообщения с кнопками внутри поста
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

                rich_message = cls._build_rich_message(
                    distribution_id=distribution_id,
                    distribution_deeplink=distribution_deeplink,
                    choices=current_choices,
                    range_start=info_distribution.range_data.start,
                    range_end=info_distribution.range_data.end,
                    choiced_index=choiced_index,
                    text=text or DEFAULT_DISTRIBUTION_TEXT,
                )

                await call.bot.edit_message_text(
                    rich_message=rich_message,
                    inline_message_id=call.inline_message_id,
                    parse_mode=None,
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

                return await cls.update_distribution_keyboard(
                    call,
                    repo,
                    distribution_id,
                    distribution_deeplink,
                    choiced_index,
                    text,
                    retry_count=retry_count + 1,
                )

            except Exception as e:
                logger.error(f"Ошибка обновления клавиатуры {distribution_id}: {e}")
                return False

    @staticmethod
    def _button_rows(
            buttons: Sequence[RichMessageButton],
            per_row: int,
    ) -> list[InputRichBlockButtons]:
        return [
            InputRichBlockButtons(buttons=list(buttons[index:index + per_row]), align="center")
            for index in range(0, len(buttons), per_row)
        ]

    @classmethod
    def _build_rich_message(
            cls,
            distribution_id: int,
            distribution_deeplink: str,
            choices: set[int],
            range_start: int,
            range_end: int,
            choiced_index: int | None = None,
            text: str = DEFAULT_DISTRIBUTION_TEXT,
    ) -> InputRichMessage:
        """Собираем rich-сообщение с кнопками внутри поста"""
        display_choices = choices | ({choiced_index} if choiced_index else set())

        auxiliary_buttons = [
            RichMessageButton(
                text=RichTextCustomEmoji(
                    custom_emoji_id="5436113877181941026",
                    alternative_text="❓",
                ),
                style=ButtonStyle.PRIMARY,
                callback_data=callback_factory.GetHelp().pack(),
            ),
            RichMessageButton(
                text="📄",
                style=ButtonStyle.PRIMARY,
                url=distribution_deeplink,
            ),
            RichMessageButton(
                text="👤",
                style=ButtonStyle.PRIMARY,
                callback_data=callback_factory.GetMyDistributionChoices(
                    distribution_id=distribution_id
                ).pack(),
            ),
        ]

        choice_buttons = []
        # range_end хранится в базе включительно, поэтому делаем +1
        for choice_index in range(range_start, range_end + 1):
            is_taken = choice_index in display_choices
            choice_buttons.append(
                RichMessageButton(
                    text=f"{choice_index} {'🔴' if is_taken else '🟢'}",
                    style=ButtonStyle.DANGER if is_taken else ButtonStyle.SUCCESS,
                    callback_data=callback_factory.MakeChoice(
                        distribution_id=distribution_id,
                        choiced_index=choice_index,
                    ).pack(),
                )
            )

        buttons_per_row = DistributionConfig().buttons_per_row
        if len(choice_buttons) >= 100:
            buttons_per_row = min(buttons_per_row, 4)

        blocks = [
            InputRichBlockParagraph(text=text),
            *cls._button_rows(auxiliary_buttons, len(auxiliary_buttons)),
            *cls._button_rows(choice_buttons, buttons_per_row),
        ]
        return InputRichMessage(blocks=blocks)
