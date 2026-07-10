import asyncio
import traceback
import time

from aiogram import Bot

from config import BOT_TOKEN

from services.coingecko import (
    get_trending_data,
    get_coin_info,
)
from services.binance_data import (
    get_open_interest,
    get_funding_rate,
)
from services.scoring import calculate_score
from services.message_builder import build_alert
from services.telegram_sender import send_alert
from services.cache import (
    funding_cache,
    oi_cache,
    sent_cache,
    CACHE_TIME,
    SENT_CACHE_TIME,
)


bot = Bot(token=BOT_TOKEN)

sent_coins = set()

previous_volumes = {}


async def check_binance_listings():

    while True:

        try:

            trending_coins = get_trending_data()

            if not trending_coins:
                print("No trending coins found.")
                await asyncio.sleep(300)
                continue

            print(f"Found {len(trending_coins)} trending coins")

            for symbol, coin in trending_coins.items():

                try:

                    symbol = symbol.upper()

                    print(f"\nChecking {symbol}")

                    rank = coin.get("rank", 9999)
                    price = coin.get("price", 0)
                    volume_raw = coin.get("volume", 0)

                    open_interest = get_open_interest(symbol)
                    funding_rate = get_funding_rate(symbol)

                    if  open_interest is None:
                        open_interest = 0

                    if  funding_rate is None:
                        funding_rate = 0.                             

                    if isinstance(volume_raw, str):
                       clean_volume = float(
                           volume_raw.replace("$", "").replace(",", "")
                     )
                    else:
                       clean_volume = float(volume_raw or 0)
                    price_change = coin.get("price_change", 0)

                    clean_market_cap = coin.get("market_cap", 0)
                    exchange_count = coin.get("exchange_count", 0)
                    top_exchanges = coin.get("top_exchanges", [])

                    previous_volume = previous_volumes.get(symbol, 0)

                    if previous_volume > 0:
                        volume_spike = (
                            (clean_volume - previous_volume)
                            / previous_volume
                        ) * 100
                    else:
                        volume_spike = 0

                    previous_volumes[symbol] = clean_volume

                    score = calculate_score(
                      rank,
                      clean_market_cap,
                      exchange_count,
                      volume_spike,
                      price_change,
                      open_interest,
                      funding_rate,
                )

                    print(
                        f"{symbol} | "
                        f"Rank: {rank} | "
                        f"Score: {score}/10 | "
                        f"Volume Spike: {volume_spike:.2f}%"
                    )

                    if score < 7:
                        print(f"Skipping {symbol} (score too low)")
                        continue

                    # coin_details = get_coin_info(coin["id"])

                    # if coin_details:
                    #  exchange_count = coin_details["exchange_count"]
                    #  top_exchanges = coin_details["top_exchanges"]

                    now = time.time()

                    if symbol in sent_cache:
                       last_sent = sent_cache[symbol]

                       if now - last_sent < SENT_CACHE_TIME:
                           print(f"Skipping {symbol} (already sent recently)")
                           continue

                    if score >= 9:
                        strength = "🟢 VERY STRONG"
                    elif score >= 8:
                        strength = "🟢 STRONG"
                    else:
                        strength = "🟡 NORMAL"

                    text = build_alert(
                      symbol=symbol,
                      rank=rank,
                      market_cap=clean_market_cap,
                      price=price,
                      volume=clean_volume,
                      volume_spike=volume_spike,
                      price_change=price_change,
                      exchange_count=exchange_count,
                      exchanges=top_exchanges,
                      score=score,
                      strength=strength,
                      funding_rate=funding_rate,
                      open_interest=open_interest,
)
                    await send_alert(text)

                    sent_coins.add(symbol)

                    sent_cache[symbol] = now 

                    print(f"Alert sent: {symbol}")

                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    traceback.print_exc()   
        except Exception as e:
            print(f"Loop error: {e}")
            traceback.print_exc()

        await asyncio.sleep(300)


async def main():
    print("Bot started...")
    await check_binance_listings()


if __name__ == "__main__":
    asyncio.run(main())          
