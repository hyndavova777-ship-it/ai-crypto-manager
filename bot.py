from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import requests
from datetime import datetime
import os
import sys
import traceback
from services.coingecko import get_trending_data
from services.binance_data import (
    get_open_interest,
    get_funding_rate,
)
from services.scoring import calculate_score
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
sent_coins = set()
previous_volumes = {}
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "🚀 Smart AI Crypto Manager активний!\n\n"
        "Команди:\n"
        "/status - статус бота\n"
        "/help - допомога"
    )


@dp.message(Command("status"))
async def status_command(message: types.Message):
    await message.answer(
        "🟢 Бот працює нормально\n"
        "📡 Binance scanner активний\n"
        "🤖 AI analysis увімкнений"
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📘 Smart AI Crypto Manager\n\n"
        "Бот шукає трендові монети Binance\n"
        "та надсилає AI alerts."
    )



# Отримати trending data
def get_trending_data_old():

    try:

        url = "https://api.coingecko.com/api/v3/search/trending"

        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {}
        
        data = response.json()

        trending = {}

        for coin in data["coins"]:

            item = coin["item"]

            symbol = item["symbol"].upper()

            rank = item.get("market_cap_rank")

            coin_data = item.get("data", {})

            volume = coin_data.get("total_volume")
            price = coin_data.get("price")
            price_change = coin_data.get("price_change_percentage_24h", {}).get("usd")

            trending[symbol] = {
                "id": item["id"],
                "rank": rank,
                "volume": volume,
                "price": price,
                "price_change": price_change
            }

        return trending

    except:
        return {}
    
def get_coin_info(coin_id):

    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        market_cap = data["market_data"]["market_cap"]["usd"]

        tickers = data.get("tickers", [])

        exchanges = []

        for ticker in tickers:
            exchange = ticker["market"]["name"]

            if exchange not in exchanges:
                exchanges.append(exchange)

        return {
            "market_cap": market_cap,
            "exchange_count": len(exchanges),
            "exchanges": exchanges[:10]
        }

    except Exception as e:
        print("CoinGecko Error:", e)
        return None


# AI scoring (simple placeholder)
def calculate_score(rank, volume, price_change):
    try:
        score = 10 - (rank or 0) / 20 + (volume or 0) / 1e6 + (price_change or 0) / 10
        return max(0, min(10, round(score, 1)))
    except Exception:
        return 0


async def check_binance_listings():
    # Placeholder loop to be implemented with real scanning logic
    while True:
        await asyncio.sleep(300)


async def main():
    print("🚀 Smart AI Crypto Manager запущений")
    asyncio.create_task(check_binance_listings())
    await dp.start_polling(bot)


asyncio.run(main())