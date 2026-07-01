from aiogram import Bot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

async def send_alert(text):
    msg = await bot.send_message(
        CHAT_ID,
        text,
        parse_mode="HTML"
    )
    print(f"MESSAGE SENT: {msg.message_id}")