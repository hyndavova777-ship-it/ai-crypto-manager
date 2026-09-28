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

def get_current_price(symbol): 
    try: 
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}" 
        response = requests.get(url, timeout=10) 
        response.raise_for_status()

        data = response.json()

        return float(data["price"])

    except Exception as e:
        print(f"Current price error for {symbol}: {e}")
        return None    

def get_price_range_after_signal(symbol, signal_time, end_time=None):
    try:
        if end_time is None: 
            end_time = time.time()

        # Аналізуємо максимум перші 60 хвилин після сигналу
        end_time = min(end_time, signal_time + 3600)

        start_ms = int(signal_time * 1000)
        end_ms = int(end_time * 1000)

        url = "https://fapi.binance.com/fapi/v1/klines"

        params = {
            "symbol": symbol,
            "interval": "1m",
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": 1000,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        candles = response.json()

        if not candles:
            return None, None

        highs = [float(candle[2]) for candle in candles]
        lows = [float(candle[3]) for candle in candles]

        max_price = max(highs)
        min_price = min(lows)

        return max_price, min_price

    except Exception as e:
        print(f"Price range error for {symbol}: {e}")
        return None, None

def get_price_momentum(symbol):
    url = "https://api.binance.com/api/v3/klines"

    def get_change(minutes):
        params = {
            "symbol": f"{symbol}USDT",
            "interval": "1m",
            "limit": minutes + 1,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return 0.0

        data = response.json()

        if len(data) < minutes + 1:
            return 0.0

        old_price = float(data[0][4])
        current_price = float(data[-1][4])

        if old_price <= 0:
            return 0.0

        return ((current_price - old_price) / old_price) * 100

    try:
        price_5m = get_change(5)
        price_15m = get_change(15)
        price_1h = get_change(60)

        return price_5m, price_15m, price_1h

    except Exception as e:
        print(f"Price momentum error for {symbol}: {e}")
        return 0.0, 0.0, 0.0


def get_volume_acceleration(symbol):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": f"{symbol}USDT",
            "interval": "5m",
            "limit": 7,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return 0.0

        data = response.json()

        if len(data) < 7:
            return 0.0

        current_volume = float(data[-2][5])
        previous_volumes = [
            float(candle[5])
            for candle in data[-7:-2]
        ]

        average_volume = sum(previous_volumes) / len(previous_volumes)

        if average_volume <= 0:
            return 0.0

        acceleration = (
            (current_volume - average_volume)
            / average_volume
        ) * 100

        return acceleration

    except Exception as e:
        print(f"Volume acceleration error for {symbol}: {e}")
        return 0.0


def get_distance_to_local_high(symbol):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": f"{symbol}USDT",
            "interval": "5m",
            "limit": 25,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return 0.0

        data = response.json()

        if len(data) < 20:
            return 0.0

        completed_candles = data[:-1]

        current_price = float(completed_candles[-1][4])

        local_high = max(
            float(candle[2])
            for candle in completed_candles[-24:]
        )

        if local_high <= 0:
            return 0.0

        distance = (
            (local_high - current_price)
            / local_high
        ) * 100

        return distance

    except Exception as e:
        print(f"Distance to local high error for {symbol}: {e}")
        return 0.0