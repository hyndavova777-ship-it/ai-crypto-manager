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

def calculate_score(
    rank,
    market_cap,
    exchange_count,
    volume_ratio,
    price_change,
    open_interest,
    funding_rate,
    rank_change 
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
    # -------------------------
    # Price Change 24h (0-1)
    # -------------------------
    if price_change is not None:
        if abs(price_change) >= 5:
            score += 1

    # -------------------------
    # Funding Rate (0-1)
    # -------------------------
    if funding_rate is not None:
        if abs(funding_rate) < 0.01:
            score += 1
        elif abs(funding_rate) < 0.03:
            score += 0.5

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