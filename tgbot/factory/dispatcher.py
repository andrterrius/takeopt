from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.i18n import I18n, ConstI18nMiddleware


from redis.asyncio import Redis

from tgbot.db.create_pool import create_pool

from tgbot.handlers.admins.admin import admin_router
from tgbot.handlers.users.user import user_router
from tgbot.handlers.users.distributions import distributions_router
from tgbot.handlers.users.query import query_router


from tgbot.middlewares.outer import DBSessionMiddleware, DBUserMiddleware

if TYPE_CHECKING:
    from aiogram.fsm.storage.base import BaseStorage

    from tgbot.config import Config


def _setup_outer_middlewares(dispatcher: Dispatcher, config: Config) -> None:
    session_pool = dispatcher["session_pool"] = create_pool(
        dsn=config.postgres.build_dsn(),
        enable_logging=config.postgres.enable_logging,
    )
    dispatcher.update.outer_middleware(DBSessionMiddleware(session_pool=session_pool))
    dispatcher.update.outer_middleware(DBUserMiddleware())

    i18n = I18n(path="locales", domain="messages")

    dispatcher.update.outer_middleware(ConstI18nMiddleware("ru", i18n)) # затычка русского языка для будущей локализации


def _setup_inner_middlewares(dispatcher: Dispatcher) -> None:
    dispatcher.callback_query.middleware(CallbackAnswerMiddleware())


def _setup_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_routers(admin_router, user_router, distributions_router, query_router)


async def create_dispatcher(config: Config) -> Dispatcher:
    storage: BaseStorage
    if config.redis.use_redis:
        storage = RedisStorage(
            redis=Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                decode_responses=True
            ),
        )
    else:
        storage = MemoryStorage()


    dispatcher: Dispatcher = Dispatcher(
        name="main_dispatcher",
        storage=storage,
        redis=storage.redis,
        config=config,
    )
    _setup_outer_middlewares(dispatcher=dispatcher, config=config)
    _setup_inner_middlewares(dispatcher=dispatcher)

    _setup_routers(dispatcher=dispatcher)


    return dispatcher
