from importlib.metadata import distribution

from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F, Router, Bot

from tgbot.db.repositories.repository import Repository
from tgbot.db.models import DBUser, DBDistribution
from tgbot.misc.logger import logger
from tgbot.core.query.query import DistributionQuery
from tgbot.core.query.exceptions import DistributionException

from tgbot.factory import callback

from sqlalchemy.ext.asyncio import AsyncSession

divider_router = Router()
divider_router.inline_query.filter(F.query)


@divider_router.inline_query()
async def inline_query(iq: InlineQuery, repo: Repository, bot: Bot) -> None:
    logger.info(await bot.me())
    text_query = iq.query

    distribution_query = DistributionQuery(text_query)
    distribution_data = distribution_query.parse_all_data()

    if isinstance(distribution_data, DistributionException):
        logger.info(distribution_data)
        articles = [InlineQueryResultArticle(
            id=text_query,
            title="Произошла ошибка.",
            description=str(distribution_data),
            input_message_content=InputTextMessageContent(
                message_text="@div_opt_bot",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        )]
    else:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"Старт",
                       callback_data=callback.CreateDistribution(query=distribution_query.get_pretty_query(),
                                                                 owner=iq.from_user.id))

        articles = [InlineQueryResultArticle(
            id=text_query,
            title="создание выбиралки",
            description=str(distribution_query.parse_all_data()),
            reply_markup=builder.as_markup(),
            input_message_content=InputTextMessageContent(
                message_text="Для запуска выбиралки нажми старт",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        )]

    await iq.answer(articles, cache_time=1)


@divider_router.callback_query(callback.CreateDistribution.filter())
async def callbacks_create_distribution(call: CallbackQuery, callback_data: callback.CreateDistribution,
                                        repo: Repository, db_user: DBUser,
                                        session: AsyncSession):
    distribution_query = DistributionQuery(call.data)
    distribution_data = distribution_query.parse_all_data()

    new_distribution = DBDistribution(creator_id=call.from_user.id, query=distribution_query.get_pretty_query(),
                                      range_data=distribution_data.range_data,
                                      count_choices=distribution_data.count_choices)
    created_distribution = await repo.distributions.save_distribution(new_distribution)
    created_distribution_id = created_distribution.id
    await session.commit()
    logger.info(created_distribution)

    builder = InlineKeyboardBuilder()
    for choice_index in range(distribution_data.range_data.start, distribution_data.range_data.end):
        builder.button(text=f"{choice_index} 🟢",
                       callback_data=callback.MakeChoice(distribution_id=created_distribution_id,
                                                         choice_index=choice_index, is_free=True))
    builder.adjust(3, repeat=True)
    await call.bot.edit_message_reply_markup(reply_markup=builder.as_markup(), inline_message_id=call.inline_message_id)
    logger.info(builder.export())


@divider_router.callback_query(callback.MakeChoice.filter())
async def callbacks_make_choice(call: CallbackQuery, callback_data: callback.MakeChoice, repo: Repository,
                                db_user: DBUser,
                                session: AsyncSession):
    logger.info(call)
    await call.answer(str(callback_data), show_alert=True)
    info_distribution = await repo.distributions.get(callback_data.distribution_id)
    logger.info(info_distribution)
    logger.info(info_distribution.creator.username)

    logger.info(db_user.distributions)


