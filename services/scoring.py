import time 

def calculate_volume_momentum(symbol, volume_ratio):
    from services.cache import volume_history

    now = time.time()

    if symbol not in volume_history:
        volume_history[symbol] = []

    volume_history[symbol].append({
        "time": now,
        "value": volume_ratio
    })

    # залишаємо тільки останні 5 записів
    volume_history[symbol] = volume_history[symbol][-5:]

    if len(volume_history[symbol]) < 2:
        return 0

    previous = volume_history[symbol][-2]["value"]

    if previous == 0:
        return 0

    change = ((volume_ratio - previous) / previous) * 100

    if change >= 50:
        return 3

    elif change >= 20:
        return 2

    elif change >= 10:
        return 1

    elif change <= -30:
        return -1

    return 0

def score_market_cap(market_cap):
    score = 0

    if market_cap <= 20_000_000:
        score += 5

    elif market_cap <= 50_000_000:
        score += 4

    elif market_cap <= 100_000_000:
        score += 3

    elif market_cap <= 250_000_000:
        score += 2

    elif market_cap <= 500_000_000:
        score += 1

    return score

def score_rank_momentum(rank_change):
    score = 0

    if rank_change >= 50:
        score += 3
    elif rank_change >= 20:
        score += 2
    elif rank_change >= 10:
        score += 1

    return score

def score_exchange_count(exchange_count):
    score = 0

    if exchange_count <= 5:
        score += 2
    elif exchange_count <= 10:
        score += 1

    return score

def score_volume_ratio(volume_ratio):
    score = 0

    if volume_ratio >= 1.50:
        score += 5

    elif volume_ratio >= 1.00:
        score += 4

    elif volume_ratio >= 0.60:
        score += 3

    elif volume_ratio >= 0.30:
        score += 2

    elif volume_ratio >= 0.15:
        score += 1

    return score
def score_open_interest_change(oi_change):
    score = 0

    if oi_change >= 20:
        score += 3

    elif oi_change >= 10:
        score += 2

    elif oi_change >= 5:
        score += 1

    elif oi_change <= -20:
        score -= 2

    elif oi_change <= -10:
        score -= 1

    return score

def calculate_score(
    rank,
    market_cap,
    exchange_count,
    volume_ratio,
    volume_momentum,
    price_change,
    open_interest,
    rank_change,
    oi_change,
):
    score = 0

    # -------------------------
    # Trending Rank (0-3)
    # -------------------------
    if rank is not None:
        if rank <= 20:
            score += 3
        elif rank <= 50:
            score += 2
        elif rank <= 100:
            score += 1

    # -------------------------
    # Market Cap (0-2)
    # -------------------------
    if market_cap is not None:
        score += score_market_cap(market_cap)
        score += score_volume_ratio(volume_ratio)
        score += score_exchange_count(exchange_count)
        score += score_open_interest_change(oi_change)
        score += volume_momentum

    # -------------------------
    # Price Change 24h (0-1)
    # -------------------------
    if price_change is not None:
        if abs(price_change) >= 5:
            score += 1

    # -------------------------
    # Open Interest Bonus (0-1)
    # -------------------------
    if open_interest is not None:
        try:
            if float(open_interest) > 0:
                score += 1
        except (ValueError, TypeError):
            pass

    # -------------------------
    # Rank Momentum (0–3)
    # -------------------------
    score += score_rank_momentum(rank_change)

    return round(min(score, 10), 1)


def calculate_pre_move_score(
    price_5m,
    price_15m,
    price_1h,
    volume_acceleration,
    oi_change,
    distance_to_high,
):
    score = 0

    # -------------------------
    # Price Momentum (0-3)
    # -------------------------
    if price_5m >= 1:
        score += 1

    if price_15m >= 2:
        score += 1

    if price_1h >= 3:
        score += 1

    # -------------------------
    # Volume Acceleration + Price Confirmation (0-3)
    # -------------------------
    if volume_acceleration >= 200:
        if price_5m > 0:
            score += 3
        elif price_15m > 0:
            score += 2
    elif volume_acceleration >= 100:
        if price_5m > 0:
            score += 2
        elif price_15m > 0:
            score += 1
    elif volume_acceleration >= 50:
        if price_5m > 0:
            score += 1

    # -------------------------
    # OI Change (0-2)
    # -------------------------
    if oi_change >= 10:
        score += 2
    elif oi_change >= 5:
        score += 1

    # -------------------------
    # Distance to Local High (0-2)
    # -------------------------
    if distance_to_high <= 2:
        score += 2
    elif distance_to_high <= 5:
        score += 1

    # -------------------------
    # Bearish protection
    # -------------------------
    if price_5m < 0 and price_1h <= -2:
        score -= 3

    return max(0, min(score, 10))