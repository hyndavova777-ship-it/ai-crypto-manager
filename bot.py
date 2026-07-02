from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import requests
from datetime import datetime
import os
import sys
import traceback
from services.coingecko import get_trending_data
from services.binance_data import get_open_interest
from services.scoring import calculate_score
from services.message_builder import build_alert

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


# AI scoring
        score = calculate_score(
    rank,
    clean_market_cap,
    exchange_count,
    volume_spike,
    price_change
)
                print(f"Checking {symbol}")
                print(
                    f"rank={rank}, "
                    f"mc={clean_market_cap}, "
                    f"ex={exchange_count}, "
                    f"price={price_change}, "
                    f"score={score}"
                )

                if rank > 100:
                    print("Skip: rank")
                    # continue

                if clean_market_cap < 50000000:
                    print("Skip: market cap")
                    # continue

                if exchange_count < 10:
                    print("Skip: exchanges")
                    # continue

                if price_change > 15:
                    print("Skip: price")
                    # continue

                if score < 8:
                    print("Skip: score")
                    # continue

                print(f"PASSED: {symbol}")

                current_time = datetime.now().strftime("%H:%M:%S")

                text = build_alert(
    symbol=symbol,
    rank=rank,
    market_cap=clean_market_cap,
    price=price,
    volume=volume,
    volume_spike=volume_spike,
    price_change=price_change,
    exchange_count=exchange_count,
    exchanges=top_exchanges,
    score=score,
    strength=strength,
)

                print(f"SENDING ALERT: {symbol}")

                try:
                    print("Trying to send...")

                    msg = await bot.send_message(
                        CHAT_ID,
                        text,
                        parse_mode="HTML"
                    )

                    print(f"MESSAGE SENT: {msg.message_id}")

                    sent_coins.add(symbol)

                except Exception as e:
                    print("SEND ERROR:")
                    print(type(e).__name__)
                    print(e)
                    traceback.print_exc()

        except Exception as e:
            print("Помилка:", e)
            traceback.print_exc()

        await asyncio.sleep(300)

async def main():

    print("🚀 Smart AI Crypto Manager запущений")

    asyncio.create_task(check_binance_listings())

    await dp.start_polling(bot)


asyncio.run(main())