from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router

from aiogram.utils.i18n import gettext as _

from tgbot.core.query.help_article import get_help_articles
from tgbot.core.query.query import DistributionQuery
from tgbot.core.query.exceptions import DistributionParserException

from tgbot.misc import callback_factory

query_router = Router()

@query_router.inline_query()
async def parse_inline_query(iq: InlineQuery) -> None:
    try:
        if not iq.query:
            raise DistributionParserException()

        text_query = iq.query.lower()

        distribution_query = DistributionQuery(text_query)
        distribution_data = distribution_query.data

        builder = InlineKeyboardBuilder()
        builder.button(text=_("Запустить распределение ✅"),
                       callback_data=callback_factory.CreateDistribution(query=distribution_query.get_pretty_query(),
                                                                         owner=iq.from_user.id))

        articles = [InlineQueryResultArticle(
            id=text_query,
            title=_("✅ Создать распределение вариантов (жми)"),
            description=_("Диапазон вариантов: {range_start} - {range_end} (включительно)"
                          "\nУ каждого будет возможность выбора {count_choices} вариантов").format(
                range_start=distribution_data.range_data.start,
                range_end=distribution_data.range_data.end,
                count_choices=distribution_data.count_choices
            ),
            reply_markup=builder.as_markup(),
            input_message_content=InputTextMessageContent(
                message_text=_("Распределение {count_options} вариантов с возможностью выбора {count_choices} вариантов").format(
                    count_options=distribution_data.range_data.end - distribution_data.range_data.start + 1,
                    count_choices=distribution_data.count_choices
                ),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        )]
        await iq.answer(articles, cache_time=1)
    except DistributionParserException as e:
        articles = await get_help_articles(iq.bot, str(e))

        await iq.answer(articles, cache_time=3)