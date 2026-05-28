from aiogram import Bot, Dispatcher, types
from aiogram. filters import Command
import asyncio
import requests
from datetime import datetime
import os

TOKEN =  os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
sent_coins = set()
bot = Bot(token=TOKEN)
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

known_symbols = set()
first_run = True


# Отримати trending data
def get_trending_data():

    try:

        url = "https://api.coingecko.com/api/v3/search/trending"

        response = requests.get(url)
        data = response.json()

        trending = {}

        for coin in data["coins"]:
            if symbol in sent_coins:
              continue

            item = coin["item"]

            symbol = item["symbol"].upper()

            rank = item.get("market_cap_rank")

            coin_data = item.get("data", {})

            volume = coin_data.get("total_volume")
            price = coin_data.get("price")
            price_change = coin_data.get("price_change_percentage_24h", {}).get("usd")

            trending[symbol] = {
                "rank": rank,
                "volume": volume,
                "price": price,
                "price_change": price_change
            }

        return trending

    except:
        return {}


# AI scoring
def calculate_score(rank, volume, price_change):

    score = 0

    # Rank
    if rank is not None:

        if rank <= 20:
            score += 4

        elif rank <= 100:
            score += 3

        elif rank <= 300:
            score += 2

    # Volume
    if volume is not None:

        if volume > 100000000:
            score += 4

        elif volume > 10000000:
            score += 3

        elif volume > 1000000:
            score += 2

    # Price change
    if price_change is not None:

        if price_change > 30:
            score += 4

        elif price_change > 15:
            score += 3

        elif price_change > 5:
            score += 2

    final_score = round(score / 1.2, 1)

    # Signal strength
    if final_score >= 8:
        strength = "🔥 VERY STRONG"

    elif final_score >= 6:
        strength = "🚀 STRONG"

    elif final_score >= 4:
        strength = "📈 MEDIUM"

    else:
        strength = "⚠️ WEAK"

    return final_score, strength


async def check_binance_listings():

    global first_run

    while True:

        try:

            trending_data = get_trending_data()

            url = "https://api.binance.com/api/v3/exchangeInfo"

            response = requests.get(url)
            data = response.json()

            symbols = data.get("symbols", [])

            for item in symbols:

                symbol = item["symbol"]

                # Тільки USDT
                if not symbol.endswith("USDT"):
                    continue

                coin_name = symbol.replace("USDT", "")

                # Тільки trending
                if coin_name not in trending_data:
                    continue

                # Нова пара
                if symbol not in known_symbols:

                    known_symbols.add(symbol)

                    if first_run:
                        continue

                    coin = trending_data[coin_name]

                    rank = coin["rank"]
                    volume = coin["volume"]
                    price = coin["price"]
                    price_change = coin["price_change"]

                    score, strength = calculate_score(
                        rank,
                        volume,
                        price_change
                    )

                    current_time = datetime.now().strftime("%H:%M:%S")

                    text = ( 
                        f"🚨 <b>SMART AI ALERT</b>\n\n"
                        f"🪙 <b>Coin:</b> {symbol}\n"
                        f"📈 <b>Exchange:</b> Binance\n"
                        f"🔥 <b>Trending:</b> YES\n"
                        f"📊 <b>Market Cap Rank:</b> #{rank}\n"
                        f"💰 <b>Price:</b> ${price:,.6f}\n"
                        f"💸 <b>Volume:</b> ${volume:,.0f}\n"
                        f"📈 <b>24h Change:</b> {price_change:.2f}%\n"
                        f"🤖 <b>AI Score:</b> {score}/10\n"
                        f"{strength}\n"
                        f"⏰ <b>Time:</b> {current_time}\n\n"
                        f"🚀 Strong market momentum detected"
                    )

                    await bot.send_message ( 
                        CHAT_ID,
                        text,
                        parse_mode="HTML"
                    )
                    sent_coins.add(symbol)

            first_run = False

        except Exception as e:
            print("Помилка:", e)

        await asyncio.sleep(60)


async def main():

    print("🚀 Smart AI Crypto Manager запущений")

    asyncio.create_task(check_binance_listings())

    await dp.start_polling(bot)


asyncio.run(main())