from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter
from tgbot.misc.logger import logger

from tgbot.db.repositories.repository import Repository

admin_router = Router()
admin_router.message.filter(AdminFilter(), F.chat.type == ChatType.PRIVATE)
admin_router.callback_query.filter(
    AdminFilter(),
    F.message.chat.type == ChatType.PRIVATE,
)

@admin_router.message(Command(commands="admin"))
async def admin_information(message: Message, state: FSMContext, repo: Repository) -> None:
    count_users = await repo.users.get_count_users()
    count_distributions = await repo.distributions.get_count_distributions()

    await message.answer(f"Всего пользователей в базе: {count_users}"
                         f"\nВсего распределений в базе: {count_distributions}")
    await state.clear()
