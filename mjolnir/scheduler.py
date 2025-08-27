import os
import json
import time
from datetime import datetime, timedelta
from .config import get_hash_rotation_days, get_baseline_hash_file, log
from .hashing import generate_baseline, compare_with_baseline

LAST_HASH_FILE = os.path.join(os.path.dirname(__file__), "last_hash_check.json")

def get_last_hash_check():
    if not os.path.exists(LAST_HASH_FILE):
        return None
    with open(LAST_HASH_FILE) as f:
        data = json.load(f)
        return datetime.fromisoformat(data.get("last_check"))

def set_last_hash_check(dt):
    with open(LAST_HASH_FILE, "w") as f:
        json.dump({"last_check": dt.isoformat()}, f)

def periodic_hash_check():
    rotation_days = get_hash_rotation_days()
    last_check = get_last_hash_check()
    now = datetime.now()

    if not last_check or (now - last_check).days >= rotation_days:
        log("Hash rotation period exceeded or never run. Running hash check...")
        generate_baseline()
        compare_with_baseline()
        set_last_hash_check(now)
    else:
        log(f"Next hash check in {rotation_days - (now - last_check).days} days.")