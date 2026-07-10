import requests
import time
from services.cache import (
    funding_cache,
    oi_cache,
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
            return None

        data = response.json()

        value = float(data["openInterest"])

        oi_cache[symbol] = {
            "value": value,
            "time": now,
        }

        return value

    except Exception:
        return None
    
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