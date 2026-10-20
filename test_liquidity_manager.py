
from services.liquidity_rebound import create_cluster_tracker
from services.liquidity_storage import save_cluster
from services.liquidity_manager import update_liquidity_clusters


test_clusters = [
    ("MANAGER_BTC_001", "BTC", 68000, 66000),
    ("MANAGER_ETH_001", "ETH", 3500, 3300),
    ("MANAGER_SOL_001", "SOL", 150, 140),
]

for cluster_id, symbol, start, end in test_clusters:
    tracker = create_cluster_tracker(
        symbol=symbol,
        cluster_start=start,
        cluster_end=end,
        observed_at=1000,
    )
    save_cluster(cluster_id, tracker)

price_updates = [
    (1010, {"BTC": 69000, "ETH": 3600, "SOL": 155}),
    (1020, {"BTC": 67000, "ETH": 3400, "SOL": 145}),
    (1030, {"BTC": 66500, "ETH": 3350, "SOL": 143}),
    (1040, {"BTC": 69000, "ETH": 3460, "SOL": 144}),
]

print("\n--- LIQUIDITY MANAGER TEST ---")

for timestamp, prices in price_updates:
    result = update_liquidity_clusters(prices, timestamp)

    print(
        f"Time: {timestamp} | "
        f"Updated: {result['updated']} | "
        f"New Target Hits: {result['target_hits']} | "
        f"Total Clusters: {result['total_clusters']}"
    )

print("\n--- TEST COMPLETE ---")
