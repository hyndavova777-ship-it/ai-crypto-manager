
import time

from services.binance_data import get_futures_prices
from services.liquidity_manager import update_liquidity_clusters
from services.liquidity_storage import load_liquidity_clusters


def update_clusters_with_live_prices():
    clusters = load_liquidity_clusters()

    active_symbols = sorted({
        tracker["symbol"]
        for tracker in clusters.values()
        if tracker["status"] in ("WAITING", "MIDPOINT_REACHED")
    })

    timestamp = time.time()

    if not active_symbols:
        return {
            "symbols": 0,
            "prices_received": 0,
            "updated": 0,
            "target_hits": 0,
            "expired": 0,
            "total_clusters": len(clusters),
        }

    prices = get_futures_prices(active_symbols)

    result = update_liquidity_clusters(
        prices=prices,
        timestamp=timestamp,
    )

    return {
        "symbols": len(active_symbols),
        "prices_received": len(prices),
        **result,
    }
