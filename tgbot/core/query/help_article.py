from aiogram import Bot

from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
from aiogram.utils.i18n import gettext as _


async def get_help_articles(bot: Bot, exception_text=""):
    bot_info = await bot.me()
    bot_username = f"@{bot_info.username}"

    exception_article = []
    if exception_text:
        exception_article.append(
            InlineQueryResultArticle(
                id="exception_article",
                title=_("❌ Произошла ошибка!"),
                description=exception_text,
                input_message_content=InputTextMessageContent(
                    message_text=bot_username,
                    parse_mode="HTML",
                )
            )
        )

    articles = [
        InlineQueryResultArticle(
        id="help",
        title=_("❓ Краткая справка по использованию бота"),
        description=_("Для создания распределения нужно ввести в строку запроса x y +z,"),
        input_message_content=InputTextMessageContent(
            message_text=bot_username,
            parse_mode="HTML",
            )
        ),
        InlineQueryResultArticle(
            id="help_2",
            title=_("ㅤ"),
            description=_("где x это начало диапазона, y - конец"),
            input_message_content=InputTextMessageContent(
                message_text=bot_username,
                parse_mode="HTML",
            )
        ),
        InlineQueryResultArticle(
            id="help_3",
            title=_("ㅤ"),
            description=_(
                "z - количество доступных выборов для 1 человека"),
            input_message_content=InputTextMessageContent(
                message_text=bot_username,
                parse_mode="HTML",
            )
        ),
        InlineQueryResultArticle(
            id="help_4",
            title=_("ㅤ"),
            description=_(
                "z по умолчанию - это 1 и ее можно не вводить это значит"),
            input_message_content=InputTextMessageContent(
                message_text=bot_username,
                parse_mode="HTML",
            )
        ),
        InlineQueryResultArticle(
            id="help_5",
            title=_("ㅤ"),
            description=_(
                "что по умолчанию можно будет выбрать только 1 вариант"),
            input_message_content=InputTextMessageContent(
                message_text=bot_username,
                parse_mode="HTML",
            )
        ),
        InlineQueryResultArticle(
            id="help_example_1",
            title=_("Пример создания простого распределения"),
            description=_("{bot_username} 1 50 - такой ввод создаст распределение вариантов от 1 до 50, где можно выбрать только 1").format(bot_username=bot_username),
            input_message_content=InputTextMessageContent(
                message_text=bot_username,
                parse_mode="HTML",
            )
        ),
        InlineQueryResultArticle(
            id="help_example_2",
            title=_("Пример создания распределения с несколькими выборами"),
            description=_(
                "{bot_username} 10 50 +2 - такой ввод создаст распределение вариантов от 10 до 50, "
                "где можно выбрать уже 2 варианта").format(bot_username=bot_username),
            input_message_content=InputTextMessageContent(
                message_text=bot_username,
                parse_mode="HTML",
            )
        ),
    ]

    return exception_article + articles