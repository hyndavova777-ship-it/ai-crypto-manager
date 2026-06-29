from aiogram import Bot, Dispatcher, types
from aiogram. filters import Command
import asyncio
import requests
from datetime import datetime
import os
import traceback

BOT_TOKEN =  os.getenv("BOT_TOKEN")
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
def get_trending_data():

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

            if symbol in sent_coins:
              continue



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
def calculate_score(rank, volume, price_change):

    score = 0

    # Rank
    try:
        rank = int(rank)
    except:
        rank = 999999

    if rank <= 20:
        score += 4
    elif rank <= 100:
        score += 3
    elif rank <= 300:
        score += 2

    # Volume
    try:
        volume = float(str(volume).replace("$", "").replace(",", ""))
    except:
        volume = 0

    if volume > 100000000:
        score += 4
    elif volume > 10000000:
        score += 3
    elif volume > 1000000:
        score += 2

    # Price change
    try:
        price_change = float(str(price_change).replace("$", "").replace(",", ""))
    except:
        price_change = 0

    if price_change > 30:
        score += 4
    elif price_change > 15:
        score += 3
    elif price_change > 5:
        score += 2

    final_score = round(score / 1.2, 1)

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

    while True:  
        try:
            trending_data = get_trending_data()

            for symbol, coin in trending_data.items():

                if symbol in sent_coins:
                    continue

                rank = coin["rank"]
                volume = coin["volume"]
                price = coin["price"]
                price_change = coin["price_change"]

                coin_info = get_coin_info(coin["id"])

                if not coin_info:
                    continue

                market_cap = coin_info["market_cap"]
                exchange_count = coin_info["exchange_count"]
                exchanges_list = coin_info["exchanges"]

                exchanges = ", ".join(exchanges_list[:5])

                # Очищаємо дані для score

                try:
                    clean_volume = float(
                        str(volume).replace("$", "").replace(",", "")
                    )
                except:
                    clean_volume = 0
                   
                try:
                    clean_market_cap = float(
                        str(market_cap).replace("$", "").replace(",", "")
                    )
                except:
                    clean_market_cap = 0
                
                volume_spike = 0

                if symbol in previous_volumes:
                    old_volume = previous_volumes[symbol]

                    if old_volume > 0:
                        volume_spike = (
                            (clean_volume - old_volume) / old_volume
                        ) * 100

                    previous_volumes[symbol] = clean_volume


                score, strength = calculate_score(
                    rank,
                    clean_volume,
                    price_change
                )

                if volume_spike > 100:
                    score += 4
                elif volume_spike > 50:
                    score += 3
                elif volume_spike > 25:
                    score += 2

                if clean_market_cap < 100000000:
                    score += 2

                if exchange_count > 10:
                    score += 1

                score = min(score, 10)

                print(
                    f"{symbol} | Rank={rank} | Volume={volume} | "
                    f"MC={market_cap} | Exchanges={exchange_count} | Score={score}"
                )

                if score < 7:
                    continue

                current_time = datetime.now().strftime("%H:%M:%S")

                text = (
                    f"🔥 <b>COINGECKO TRENDING ALERT</b>\n\n"
                    f"🪙 <b>Coin:</b> {symbol}\n"
                    f"📊 <b>Trending Rank:</b> #{rank}\n"
                    f"💎 <b>Market Cap:</b> {market_cap}\n"
                    f"💰 <b>Price:</b> ${price:,.6f}\n"
                    f"💸 <b>Volume:</b> {volume}\n"
                    f"📊 <b>Volume Spike:</b> {volume_spike:.1f}%\n"
                    f"📈 <b>24h Change:</b> {price_change:.2f}%\n"
                    f"🏦 <b>Listed On:</b> {exchange_count} exchanges\n"
                    f"📈 <b>Top Exchanges:</b> {exchanges}\n\n"
                    f"🤖 <b>AI Score:</b> {score}/10\n"
                    f"{strength}\n"
                    f"⏰ <b>Time:</b> {current_time}"
                )

                print(f"SENDING ALERT: {symbol}")

                await bot.send_message(
                    CHAT_ID,
                    text,
                    parse_mode="HTML"
                )

                sent_coins.add(symbol)

        except Exception as e:
            print("Помилка:", e)
            traceback.print_exc()

        await asyncio.sleep(300)

async def main():

    print("🚀 Smart AI Crypto Manager запущений")

    asyncio.create_task(check_binance_listings())

    await dp.start_polling(bot)


asyncio.run(main())