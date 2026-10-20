
import json
import os
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

DATA_FILE = DATA_DIR / (
    "liquidity_clusters_test.json"
    if os.getenv("LIQUIDITY_TEST_MODE") == "1"
    else "liquidity_clusters.json"
)


def load_liquidity_clusters():
    """Завантажує збережені кластери."""
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Invalid cluster storage format")

        return data

    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Liquidity storage error: {error}")
        raise


def save_liquidity_clusters(clusters):
    """Безпечно зберігає кластери у JSON."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = DATA_FILE.with_suffix(".json.tmp")

    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                clusters,
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_file, DATA_FILE)

    finally:
        if temp_file.exists():
            temp_file.unlink()


def save_cluster(cluster_id, tracker):
    """Зберігає один кластер за його ID."""
    clusters = load_liquidity_clusters()
    clusters[cluster_id] = tracker
    save_liquidity_clusters(clusters)


def get_cluster(cluster_id):
    """Повертає раніше збережений кластер."""
    clusters = load_liquidity_clusters()
    return clusters.get(cluster_id)

