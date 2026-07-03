import asyncio
import traceback

from aiogram import Bot

from config import BOT_TOKEN

from services.coingecko import (
    get_trending_coins,
    get_coin_info,
)

from services.binance_data import (
    get_open_interest,
    get_funding_rate,
)

from services.scoring import calculate_score

from services.message_builder import build_alert

from services.telegram_sender import send_alert
bot = Bot(token=BOT_TOKEN)
sent_coins = set()

previous_volumes = {}
async def check_binance_listings():
    while True:
        try:
            trending_coins = get_trending_coins()

            if not trending_coins:
                print("No trending coins found.")
                await asyncio.sleep(300)
                continue

            print(f"Found {len(trending_coins)} trending coins")

            for coin in trending_coins:
                
                try:
                    symbol = coin["symbol"].upper()

                    print(f"\nChecking {symbol}")

                    coin_info = get_coin_info(symbol)

                    if not coin_info:
                        print(f"No CoinGecko data for {symbol}")
                        continue

                    rank = coin_info["rank"]
                    clean_market_cap = coin_info["market_cap"]
                    price = coin_info["price"]
                    clean_volume = coin_info["volume"]
                    exchange_count = coin_info["exchange_count"]
                    top_exchanges = coin_info["top_exchanges"]

                    previous_volume = previous_volumes.get(symbol, 0)

                    if previous_volume > 0:
                        volume_spike = (
                            (clean_volume - previous_volume)
                            / previous_volume
                        ) * 100
                    else:
                        volume_spike = 0

                    previous_volumes[symbol] = clean_volume

                    price_change = coin_info["price_change"]

                    open_interest = get_open_interest(symbol)
                    funding_rate = get_funding_rate(symbol)

                    strength = "🟢 Strong"
                    score = calculate_score(
                        rank,
                        clean_market_cap,
                        exchange_count,
                        volume_spike,
                        price_change,
                    )

                    print(
                        f"{symbol} | "
                        f"Rank: {rank} | "
                        f"Score: {score}/10 | "
                        f"Volume Spike: {volume_spike:.2f}%"
                    )

                    if score < 8:
                        print(f"Skipping {symbol} (score too low)")
                        continue

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
                    )

                    await send_alert(text)

                    sent_coins.add(symbol)

                    print(f"Alert sent: {symbol}")
                
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    traceback.print_exc() 

        except Exception as e:
            print(f"Loop error: {e}")
            traceback.print_exc()

    await asyncio.sleep(300)
       
async def main():
    await check_binance_listings()


if __name__== "__main__":
    asyncio.run(main())
            
