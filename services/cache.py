import time

funding_cache = {}
oi_cache = {}
previous_open_interest = {}
volume_history = {}


CACHE_TIME = 120  # секунд

sent_cache = {}

SENT_CACHE_TIME = 60 * 60 * 24  # 24 години