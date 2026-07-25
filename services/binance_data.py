import requests
import time
from services.cache import (
    funding_cache,
    oi_cache,
    previous_open_interest,
    CACHE_TIME,
)

def get_open_interest(symbol):

    now = time.time()

    if symbol in oi_cache:
        cached = oi_cache[symbol]

        if now - cached["time"] < CACHE_TIME:
            return cached["value"]

    try:
        url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}USDT"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None, 0 

        data = response.json()

        value = float(data["openInterest"])

        previous = previous_open_interest.get(symbol, value)

        oi_change = 0

        if previous > 0:
            oi_change = ((value - previous) / previous) * 100

        previous_open_interest[symbol] = value

        oi_cache[symbol] = {
            "value": (value, oi_change),
            "time": now,
        }

        return value, oi_change

    except Exception:
        return None, 0

def get_funding_rate(symbol):

    now = time.time()

    if symbol in funding_cache:
        cached = funding_cache[symbol]

        if now - cached["time"] < CACHE_TIME:
            return cached["value"]

    try:
        url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}USDT"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        value = float(data["lastFundingRate"])

        funding_cache[symbol] = {
            "value": value,
            "time": now,
        }

        return value

    except Exception:
        return None 