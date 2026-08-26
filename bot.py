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
    get_price_momentum,
    get_volume_acceleration,
)
from services.scoring import calculate_score, calculate_volume_momentum
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
previous_ranks = {}
previous_volumes = {}

def has_too_many_bearish_signals(
    volume_momentum,
    rank_change,
    price_change,
    oi_change,
):
    bearish_signals = 0

    if volume_momentum < 0:
        bearish_signals += 1

    if rank_change < 0:
        bearish_signals += 1

    if price_change < 0:
        bearish_signals += 1

    if oi_change < 0:
        bearish_signals += 1

    return bearish_signals >= 3

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

                    rank = coin.get("rank", 9999)
                    price = coin.get("price", 0)
                    volume_raw = coin.get("volume", 0)

                    previous_rank = previous_ranks.get(symbol, rank)

                    rank_change = previous_rank - rank

                    old_rank = previous_rank

                    previous_ranks[symbol] = rank

                    open_interest, oi_change = get_open_interest(symbol)

                    price_5m, price_15m, price_1h = get_price_momentum(symbol)

                    volume_acceleration = get_volume_acceleration(symbol)

                    if has_bearish_price_momentum(
                        price_5m,
                        price_15m,
                        price_1h,
   ):
                        print(f"Skipping {symbol} (bearish price momentum)")
                        continue
                    
                    if  open_interest is None:
                        open_interest = 0                          

                    if isinstance(volume_raw, str):
                       clean_volume = float(
                           volume_raw.replace("$", "").replace(",", "")
                     )
                    else:
                       clean_volume = float(volume_raw or 0)
                    price_change = coin.get("price_change", 0)

                    clean_market_cap = coin.get("market_cap", 0)

                    if clean_market_cap > 0:
                        volume_ratio = clean_volume / clean_market_cap
                    else:
                        volume_ratio = 0

                    # Skip very large coins
                    if clean_market_cap > 5_000_000_000:
                        print(f"Skipping {symbol} (market cap too high)")
                        continue
                    exchange_count = coin.get("exchange_count", 0)
                    top_exchanges = coin.get("top_exchanges", [])

                    volume_momentum = calculate_volume_momentum(
                        symbol,
                        volume_ratio
  )

                    if has_too_many_bearish_signals(
                      volume_momentum,
                      rank_change,
                       price_change,
                       oi_change,
            ):
                       print(f"Skipping {symbol} (too many bearish signals)")
                       continue

                    score = calculate_score( 
                      rank,
                      clean_market_cap,
                      exchange_count,
                      volume_ratio,
                      volume_momentum,
                      price_change,
                      open_interest,
                      rank_change,
                      oi_change,
                      
                 )

                    print(
                        f"{symbol} | "
                        f"Rank: {rank} | "
                        f"Rank Momentum: {rank_change} | "
                        f"Volume Ratio: {volume_ratio:.2f}% | "
                        f"Volume Momentum: {volume_momentum} | "
                        f"Score: {score}/10"
                        f"Price Momentum: 5m {price_5m:+.2f}% | "
                        f"15m {price_15m:+.2f}% | "
                        f"1h {price_1h:+.2f}% | "
                        f"Volume Acceleration: {volume_acceleration:+.2f}% | "
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
                      volume_ratio=volume_ratio,
                      volume_momentum=volume_momentum,
                      price_change=price_change,
                      exchange_count=exchange_count,
                      exchanges=top_exchanges,
                      score=score,
                      strength=strength,
                      open_interest=open_interest,
                      oi_change=oi_change,
                      old_rank=old_rank,
                      current_rank=rank,
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
