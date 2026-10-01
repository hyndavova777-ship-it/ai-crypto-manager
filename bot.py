import asyncio
import traceback
import time
import json
import os
from abc import ABC, abstractmethod

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
    get_price_range_after_signal,
    get_historical_price, 
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
    pre_move_breakdown, 
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

            "price_score": pre_move_breakdown["price_score"],
            "volume_score": pre_move_breakdown["volume_score"],
            "oi_score": pre_move_breakdown["oi_score"],
            "distance_score": pre_move_breakdown["distance_score"],
            "confluence_score": pre_move_breakdown["confluence_score"],
            "bearish_penalty": pre_move_breakdown["bearish_penalty"],

            "price_5m": price_5m,
            "price_15m": price_15m,
            "price_1h": price_1h,

            "volume_acceleration": volume_acceleration,
            "distance_to_high": distance_to_high,
            "oi_change": oi_change,

            # Outcome Tracker
            "price_after_15m": None,
            "change_after_15m": None,

            "price_after_30m": None,
            "change_after_30m": None,

            "price_after_60m": None,
            "change_after_60m": None,

            "max_price_60m": None,
            "max_change_60m": None,

            "min_price_60m": None,
            "min_change_60m": None,

            "outcome_complete": False,
        }

        history.append(signal)

        with open(SIGNAL_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

        print(f"Signal history saved: {symbol}")

    except Exception as e:
        print(f"Error saving signal history for {symbol}: {e}")

def update_signal_outcomes(): 
    try: 
        with open(SIGNAL_HISTORY_FILE, "r") as f: 
            history = json.load(f) 
    except (FileNotFoundError, json.JSONDecodeError): 
        return   
    current_time = time.time()
    history_changed = False

    for signal in history:

        if "outcome_complete" not in signal:
            continue

        if signal.get("outcome_complete", False):
            continue

        signal_time = signal.get("time")
        signal_price = signal.get("signal_price")
        symbol = signal.get("symbol")

        if not signal_time or not signal_price or not symbol:
            continue

        open_interest, _ = get_open_interest(symbol)

        if open_interest is None:
            signal["outcome_complete"] = True
            signal["outcome_error"] = "no_binance_futures"
            history_changed = True
            continue

        elapsed_minutes = (current_time - signal_time) / 60

        if ( 
            elapsed_minutes >= 15 
            and signal.get("price_after_15m") is None 
        ): 
            price_15m_after = get_historical_price( 
                symbol, 
                signal_time + (15 * 60), 
            )

            if price_15m_after is not None:
                signal["price_after_15m"] = price_15m_after
                signal["change_after_15m"] = (
                    (price_15m_after - signal_price) / signal_price
                ) * 100

                history_changed = True

        if ( 
            elapsed_minutes >= 30 
            and signal.get("price_after_30m") is None 
        ): 
            price_30m_after = get_historical_price( 
                symbol, 
                signal_time + (30 * 60), 
            )

            if price_30m_after is not None:
                signal["price_after_30m"] = price_30m_after
                signal["change_after_30m"] = (
                    (price_30m_after - signal_price) / signal_price
                ) * 100

                history_changed = True

        if ( 
            elapsed_minutes >= 60 
            and signal.get("price_after_60m") is None 
        ):
            price_60m_after = get_historical_price( 
                symbol, 
                signal_time + (60 * 60), 
            )

            if price_60m_after is not None:
                signal["price_after_60m"] = price_60m_after
                signal["change_after_60m"] = (
                    (price_60m_after - signal_price) / signal_price
                ) * 100

                max_price, min_price = get_price_range_after_signal(
                    symbol=symbol,
                    signal_time=signal_time,
                    end_time=signal_time + 3600,
                )

                if max_price is not None:
                    signal["max_price_60m"] = max_price
                    signal["max_change_60m"] = (
                        (max_price - signal_price) / signal_price
                    ) * 100

                if min_price is not None:
                    signal["min_price_60m"] = min_price
                    signal["min_change_60m"] = (
                        (min_price - signal_price) / signal_price
                    ) * 100

                signal["outcome_complete"] = True
                history_changed = True

    if history_changed:
        with open(SIGNAL_HISTORY_FILE, "w") as f: 
            json.dump(history, f, indent=4)

def has_bearish_price_momentum(price_5m, price_15m, price_1h): 
    if price_5m < 0 and price_1h <= -2: 
        return True
    
    return False


async def check_binance_listings():

    while True:

        try:

            # Update outcomes of previously sent signals
            update_signal_outcomes()

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
                        pre_move_breakdown=pre_move_breakdown,
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
