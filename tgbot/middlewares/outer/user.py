from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User

from tgbot.db.models import DBUser

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tgbot.db.repositories.repository import Repository

from tgbot.misc.logger import logger


class DBUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event = cast(Update, event)
        aiogram_user: User = data["event_from_user"]
        repo: Repository = data["repo"]
        user = await repo.users.get_or_update_user(
            user_id=aiogram_user.id,
            name=aiogram_user.full_name,
            username=aiogram_user.username
        )

        data["db_user"] = user

        return await handler(event, data)
