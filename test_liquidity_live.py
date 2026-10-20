
from services.binance_data import get_futures_prices

symbols = ["BTC", "ETH", "SOL"]

prices = get_futures_prices(symbols)

print("\n--- LIVE LIQUIDITY CONNECTION ---")

for symbol in symbols:
    price = prices.get(symbol)

    if price is None:
        print(f"{symbol} | NO DATA")
    else:
        print(f"{symbol} | ${price:,.4f} | CONNECTED")

print("\n--- CONNECTION TEST COMPLETE ---")
