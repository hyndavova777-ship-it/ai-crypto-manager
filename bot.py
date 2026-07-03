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
                    
