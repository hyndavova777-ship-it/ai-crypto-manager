
from services.btc_cluster_detector import (
    detect_btc_clusters,
)

BTC_PRICE = 80_000

# Умовні дані, НЕ реальна карта CoinGlass.
levels = [
    {"price": 79900, "size_usdt": 120000},
    {"price": 79800, "size_usdt": 350000},
    {"price": 79700, "size_usdt": 480000},

    # Перший кластер
    {"price": 79600, "size_usdt": 530000},
    {"price": 79500, "size_usdt": 650000},
    {"price": 79400, "size_usdt": 720000},
    {"price": 79300, "size_usdt": 510000},

    # Рівень нижче порога розділяє кластери
    {"price": 79200, "size_usdt": 480000},

    # Другий кластер
    {"price": 79100, "size_usdt": 600000},
    {"price": 79000, "size_usdt": 550000},

    {"price": 78900, "size_usdt": 200000},
]

clusters = detect_btc_clusters(
    levels=levels,
    current_price=BTC_PRICE,
)

print("\n--- BTC CLUSTER DETECTOR TEST ---")
print(f"BTC Price: ${BTC_PRICE:,.2f}")
print(f"Accepted Clusters: {len(clusters)}")

for index, cluster in enumerate(clusters, 1):
    print(f"\nCluster #{index}")
    print(
        "Range:",
        f"${cluster['cluster_start']:,.2f}"
        f" - ${cluster['cluster_end']:,.2f}",
    )
    print(
        "Midpoint:",
        f"${cluster['cluster_midpoint']:,.2f}",
    )
    print(
        "Total liquidity:",
        f"${cluster['cluster_size_usdt']:,.0f}",
    )
    print(
        "Minimum level liquidity:",
        f"${cluster['min_level_size_usdt']:,.0f}",
    )

assert len(clusters) == 2

assert clusters[0]["cluster_start"] == 79600
assert clusters[0]["cluster_end"] == 79300
assert clusters[0]["cluster_midpoint"] == 79450
assert clusters[0]["cluster_size_usdt"] == 2410000

assert clusters[1]["cluster_start"] == 79100
assert clusters[1]["cluster_end"] == 79000
assert clusters[1]["cluster_size_usdt"] == 1150000

assert all(
    cluster["min_level_size_usdt"] >= 500000
    for cluster in clusters
)

print("\n--- TEST PASSED ---")

