from aiogram import F, Router, types
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, SwitchInlineQueryChosenChat
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from tgbot.misc.logger import logger
from tgbot.db.models.user import DBUser

from tgbot.db.repositories.repository import Repository

from aiogram.utils.i18n import gettext as _

user_router = Router()
user_router.message.filter(F.chat.type == ChatType.PRIVATE)
user_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

@user_router.message()
async def all_messages(message: Message) -> None:
    bot_info = await message.bot.me()
    bot_username = f"@{bot_info.username}"

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(types.InlineKeyboardButton(
        text=_("Выбрать чат"), switch_inline_query="")
    )

    await message.answer(_(
        "Привет, бот работает в инлайн режиме. "
        "Для использования пропиши {bot_username} в любом чате/канале или нажми на кнопку ниже").format(bot_username=bot_username),
                         reply_markup=keyboard_builder.as_markup())