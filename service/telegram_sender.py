from aiogram import Bot

from ..config import CHAT_ID


async def send_alert(bot: Bot, text: str):
    msg = await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="HTML"
    )
    return msg