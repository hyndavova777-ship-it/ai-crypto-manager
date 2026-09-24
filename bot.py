import asyncio
import traceback
import time
import json
import os

from aiogram import Bot

from config import BOT_TOKEN

from services.scoring import calculate_pre_move_score

from services.coingecko import (
    get_trending_data,
    get_coin_info,
)
from services.binance_data import (
    get_open_interest,
    get_funding_rate,
    get_price_momentum,
    get_volume_acceleration,
    get_distance_to_local_high,
)
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

SIGNAL_HISTORY_FILE = "data/signal_history.json"


def save_signal_history(
    symbol,
    signal_price,
    pre_move_score,
    price_5m,
    price_15m,
    price_1h,
    volume_acceleration,
    distance_to_high,
    oi_change,
):
    try:
        os.makedirs("data", exist_ok=True)

        if os.path.exists(SIGNAL_HISTORY_FILE):
            with open(SIGNAL_HISTORY_FILE, "r") as f:
                history = json.load(f)
        else:
            history = []

        signal = {
            "symbol": symbol,
            "time": time.time(),
            "signal_price": signal_price,
            "pre_move_score": pre_move_score,
            "price_5m": price_5m,
            "price_15m": price_15m,
            "price_1h": price_1h,
            "volume_acceleration": volume_acceleration,
            "distance_to_high": distance_to_high,
            "oi_change": oi_change,
        }

        history.append(signal)

        with open(SIGNAL_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

        print(f"Signal history saved: {symbol}")

    except Exception as e:
        print(f"Error saving signal history for {symbol}: {e}")

def has_bearish_price_momentum(price_5m, price_15m, price_1h): 
    if price_5m < 0 and price_1h <= -2: 
        return True
    
    return False


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

                    price = coin.get("price", 0)

                    _, oi_change = get_open_interest(symbol)

                    price_5m, price_15m, price_1h = get_price_momentum(symbol)

                    volume_acceleration = get_volume_acceleration(symbol)

                    distance_to_high = get_distance_to_local_high(symbol)

                    pre_move_score = calculate_pre_move_score(
                        price_5m,
                        price_15m,
                        price_1h,
                        volume_acceleration,
                        oi_change,
                        distance_to_high,
                    )
                    pre_move_breakdown = pre_move_score
                    pre_move_score = pre_move_breakdown["score"]

                    if has_bearish_price_momentum(
                        price_5m,
                        price_15m,
                        price_1h,
   ):
                        print(f"Skipping {symbol} (bearish price momentum)")
                        continue                          

                    print(
                        f"{symbol} | "
                        f"Price Momentum: 5m {price_5m:+.2f}% | "
                        f"15m {price_15m:+.2f}% | "
                        f"1h {price_1h:+.2f}% | "
                        f"Volume Acceleration: {volume_acceleration:+.2f}% | "
                        f"Pre-Move Score: {pre_move_score}/10 | "
                        f"Distance to High: {distance_to_high:.2f}% | "
                    )

                    if pre_move_score < 5:
                        print(
                            f"Skipping {symbol} "
                            f"(Pre-Move Score too low: {pre_move_score}/10)"
                        )
                        continue

                    # coin_details = get_coin_info(coin["id"])

                    # if coin_details:

                    now = time.time()

                    if symbol in sent_cache:
                       last_sent = sent_cache[symbol]

                       if now - last_sent < SENT_CACHE_TIME:
                           print(f"Skipping {symbol} (already sent recently)")
                           continue

                    text = build_alert(
                       symbol=symbol,
                       price=price,
                       pre_move_score=pre_move_score,
                       pre_move_breakdown=pre_move_breakdown,
                       oi_change=oi_change,
                    )
                    save_signal_history(
                        symbol=symbol,
                        signal_price=price,
                        pre_move_score=pre_move_score,
                        price_5m=price_5m,
                        price_15m=price_15m,
                        price_1h=price_1h,
                        volume_acceleration=volume_acceleration,
                        distance_to_high=distance_to_high,
                        oi_change=oi_change,
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

        await asyncio.sleep(900)


async def main():
    print("Bot started...")
    await check_binance_listings()


if __name__ == "__main__":
    asyncio.run(main())          
