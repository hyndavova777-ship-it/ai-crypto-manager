def calculate_score(
    rank,
    market_cap,
    exchange_count,
    volume_ratio,
    price_change,
    open_interest,
    funding_rate,
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
        if market_cap >= 1_000_000_000:
            score += 2
        elif market_cap >= 100_000_000:
            score += 1

    # -------------------------
        # Volume quality
    if volume_ratio >= 0.50:
        score += 3
    elif volume_ratio >= 0.30:
        score += 2
    elif volume_ratio >= 0.15:
        score += 1
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

    return round(min(score, 10), 1)