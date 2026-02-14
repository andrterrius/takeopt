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
            escaped_name = html.escape(user.full_name)
            return f'<a href="tg://user?id={user_id}">{escaped_name}</a>'
        else:
            return str(user_id)

    except:
        return str(user_id)