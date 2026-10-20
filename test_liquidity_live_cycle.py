
import os
import time

# Захищаємо робочу історію від тестових записів.
os.environ["LIQUIDITY_TEST_MODE"] = "1"

from services.binance_data import get_futures_prices
from services.liquidity_rebound import create_cluster_tracker
from services.liquidity_storage import save_cluster, get_cluster
from services.liquidity_live import update_clusters_with_live_prices


print("\n--- LIVE CYCLE TEST ---")

prices = get_futures_prices(["BTC"])

if "BTC" not in prices:
    raise RuntimeError("BTC Futures price unavailable")

current_price = prices["BTC"]

# Умовний кластер нижче поточної ціни.
# Це НЕ реальний кластер ліквідацій.
cluster_start = current_price * 0.99
cluster_end = current_price * 0.97

cluster_id = "TEST_LIVE_BTC_001"

tracker = create_cluster_tracker(
    symbol="BTC",
    cluster_start=cluster_start,
    cluster_end=cluster_end,
    observed_at=time.time(),
)

save_cluster(cluster_id, tracker)

print(f"BTC Price: ${current_price:,.2f}")
print(
    f"Test Cluster: "
    f"${cluster_start:,.2f}-${cluster_end:,.2f}"
)

result = update_clusters_with_live_prices()

restored = get_cluster(cluster_id)

print("\n--- MANAGER RESULT ---")
print("Prices Received:", result["prices_received"])
print("Clusters Updated:", result["updated"])
print("Target Hits:", result["target_hits"])
print("Expired:", result["expired"])

print("\n--- BTC CLUSTER ---")
print("Status:", restored["status"])
print(
    "Above Midpoint Seen:",
    restored["price_above_midpoint_seen"]
)

assert result["prices_received"] >= 1
assert restored["status"] == "WAITING"

print("\n--- TEST PASSED ---")
