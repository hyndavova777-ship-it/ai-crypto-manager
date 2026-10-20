
from services.liquidity_rebound import (
    create_cluster_tracker,
    update_cluster_tracker,
)
from services.liquidity_storage import (
    save_cluster,
    get_cluster,
)

test_cases = [
    {
        "id": "TEST_BTC_001",
        "symbol": "BTC",
        "start": 68000,
        "end": 66000,
        "prices": [69000, 67000, 66500, 69000],
    },
    {
        "id": "TEST_ETH_001",
        "symbol": "ETH",
        "start": 3500,
        "end": 3300,
        "prices": [3600, 3400, 3350, 3460],
    },
    {
        "id": "TEST_SOL_001",
        "symbol": "SOL",
        "start": 150,
        "end": 140,
        "prices": [155, 145, 143, 144],
    },
]

print("\n--- MULTIPLE CLUSTERS TEST ---")

for case in test_cases:
    tracker = create_cluster_tracker(
        symbol=case["symbol"],
        cluster_start=case["start"],
        cluster_end=case["end"],
        observed_at=1000,
    )

    # Кожне спостереження відділене 10 секундами
    for index, price in enumerate(case["prices"]):
        timestamp = 1010 + index * 10
        tracker = update_cluster_tracker(
            tracker, price, timestamp
        )

    save_cluster(case["id"], tracker)

    restored = get_cluster(case["id"])

    print(
        f"{case['symbol']} | "
        f"Cluster: ${case['start']:,.2f}-${case['end']:,.2f} | "
        f"Coin Price: ${case['prices'][-1]:,.2f} | "
        f"Status: {restored['status']} | "
        f"Rebound: {restored['rebound_pct']:.2f}%"
    )

print("\n--- TEST COMPLETE ---")
