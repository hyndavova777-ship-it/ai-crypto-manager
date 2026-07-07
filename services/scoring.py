def calculate_score(
    rank,
    market_cap,
    exchange_count,
    volume_spike,
    price_change,
    open_interest,
    funding_rate,
):
    score = 0

    # Trending Rank
    if rank <= 10:
        score += 4
    elif rank <= 30:
        score += 3
    elif rank <= 60:
        score += 2
    elif rank <= 100:
        score += 1

    # Market Cap
    if market_cap < 100_000_000:
        score += 2
    elif market_cap < 500_000_000:
        score += 1

    # Біржі
    if exchange_count > 20:
        score += 2
    elif exchange_count > 10:
        score += 1

    # Volume Spike
    if volume_spike > 100:
        score += 3
    elif volume_spike > 50:
        score += 2
    elif volume_spike > 25:
        score += 1

    # Price Change
    if 0 < price_change < 10:
        score += 1
        # Open Interest
    if open_interest is not None and open_interest > 0:
        score += 1

    # Funding Rate
    if funding_rate is not None and abs(funding_rate) < 0.01:
        score += 1

    return min(score, 10)