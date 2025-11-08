import html
from aiogram import Bot

async def get_telegram_username(bot: Bot, user_id: int) -> str:
    """
    Получает username или full_name пользователя Telegram"""
    try:
        user = await bot.get_chat(user_id)

        if user.username:
            return f"@{user.username}"
        elif user.full_name:
            return html.escape(user.full_name)
        else:
            return str(user_id)

    except:
        return str(user_id)