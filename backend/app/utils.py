import os
import json
from datetime import datetime, timedelta

CACHE_FILE = "/app/cache/cache.json"
CACHE_EXPIRY_HOURS = 24

def charger_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def sauvegarder_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def est_cache_valide(cache_entry):
    if "timestamp" not in cache_entry:
        return False
    timestamp = datetime.fromisoformat(cache_entry["timestamp"])
    return (datetime.now() - timestamp) < timedelta(hours=CACHE_EXPIRY_HOURS)