
from datetime import datetime
from zoneinfo import ZoneInfo

from services.binance_data import get_futures_prices


symbols = ["BTC", "ETH", "SOL"]

prices = get_futures_prices(symbols)

kyiv_time = datetime.now(
    ZoneInfo("Europe/Kyiv")
).strftime("%d.%m.%Y %H:%M:%S")

print("\n--- BINANCE FUTURES PRICES ---")
print("Kyiv Time:", kyiv_time)

for symbol in symbols:
    price = prices.get(symbol)

    if price is None:
        print(f"{symbol} | Price unavailable")
    else:
        print(f"{symbol} | ${price:,.4f}")

print("\n--- TEST COMPLETE ---")
