import time

from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F, Router, Bot

from tgbot.db.repositories.repository import Repository
from tgbot.db.models import DBUser, DBDistribution, DBChoice
from tgbot.misc.logger import logger
from tgbot.core.query.query import DistributionQuery
from tgbot.core.query.exceptions import DistributionException

from tgbot.factory import callback

from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

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
    distribution_query = DistributionQuery(callback_data.query)
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
                                                         choiced_index=choice_index))
    builder.adjust(3, repeat=True)
    await call.bot.edit_message_reply_markup(reply_markup=builder.as_markup(), inline_message_id=call.inline_message_id)


@divider_router.callback_query(callback.MakeChoice.filter())
async def callbacks_make_choice(call: CallbackQuery, callback_data: callback.MakeChoice, repo: Repository,
                                session: AsyncSession, redis: Redis):
    user_id = call.from_user.id
    distribution_id = callback_data.distribution_id
    choiced_index = callback_data.choiced_index

    user_key = f"distribution:user:{distribution_id}:{user_id}"
    choice_key = f"distribution:choice:{distribution_id}:{choiced_index}"
    limit_key = f"limit:distribution:{distribution_id}"

    max_choices = await redis.get(limit_key)
    info_distribution = None

    if not max_choices:
        info_distribution = await repo.distributions.get(distribution_id)
        max_choices = info_distribution.count_choices
        await redis.set(limit_key, max_choices, ex=300)
    else:
        max_choices = int(max_choices)

    user_current_choices = int(await redis.get(user_key) or 0)
    if user_current_choices >= max_choices:
        return await call.answer(f"Вы уже выбрали вариант!", show_alert=True)

    reservation = await redis.set(choice_key, user_id, ex=5, nx=True)

    if reservation:
        try:
            await redis.set(user_key, choiced_index, ex=60)

            if not info_distribution:
                info_distribution = await repo.distributions.get(distribution_id)

            new_choice = DBChoice(distribution_id=distribution_id, button_index=choiced_index, user_id=user_id)
            await repo.choices.create(new_choice)

            await call.answer(f"✅ Вы выбрали вариант {choiced_index}!", show_alert=True)
            await redis.set(user_key, user_current_choices+1)

            all_choices = await repo.choices.get_all_choices_indexes(distribution_id=distribution_id)
            all_choices.add(choiced_index)
            logger.info(info_distribution.query)

            builder = InlineKeyboardBuilder()
            for choice_index in range(info_distribution.range_data.start, info_distribution.range_data.end):
                builder.button(text=f"{choice_index} " + ("🔴" if choice_index in all_choices else "🟢"),
                               callback_data=callback.MakeChoice(distribution_id=distribution_id,
                                                                 choiced_index=choice_index))

            builder.adjust(3)
            await call.bot.edit_message_reply_markup(reply_markup=builder.as_markup(), inline_message_id=call.inline_message_id)

        except Exception as e:
            await redis.delete(choice_key)
            raise e
        finally:
            await session.commit()
    else:
        current_owner = await redis.get(choice_key)
        if current_owner and current_owner == str(user_id):
            await call.answer("Вы уже занимаете этот вариант!", show_alert=True)
        else:
            await call.answer("Кнопка временно занята, повторите через несколько секунд!", show_alert=True)

    return
    await call.answer(str(callback_data), show_alert=True)
    info_distribution = await repo.distributions.get(callback_data.distribution_id)
    logger.info(info_distribution)
    logger.info(info_distribution.creator.username)

    logger.info(db_user.distributions)
