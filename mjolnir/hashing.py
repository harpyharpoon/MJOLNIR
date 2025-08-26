import os
import hashlib
import json
from .config import BASELINE_HASH_FILE, get_mandatory_files, log

def hash_file(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        log(f"[!] Could not hash {filepath}: {e}")
        return None

def generate_baseline():
    hashes = {}
    for category, files in get_mandatory_files().items():
        hashes[category] = {}
        for f in files:
            if os.path.exists(f):
                if os.path.isdir(f):
                    for root, _, filenames in os.walk(f):
                        for fn in filenames:
                            path = os.path.join(root, fn)
                            hashes[category][path] = hash_file(path)
                else:
                    hashes[category][f] = hash_file(f)
    with open(BASELINE_HASH_FILE, "w") as bf:
        json.dump(hashes, bf, indent=2)
    log(f"Baseline hashes written to {BASELINE_HASH_FILE}")

def compare_with_baseline():
    if not os.path.exists(BASELINE_HASH_FILE):
        log("[!] No baseline hash file found.")
        return

    with open(BASELINE_HASH_FILE, "r") as bf:
        baseline = json.load(bf)

    mismatches = []
    for category, files in get_mandatory_files().items():
        for f in files:
            if os.path.exists(f):
                if os.path.isdir(f):
                    for root, _, filenames in os.walk(f):
                        for fn in filenames:
                            path = os.path.join(root, fn)
                            current = hash_file(path)
                            expected = baseline.get(category, {}).get(path)
                            if expected and current != expected:
                                mismatches.append((path, expected, current))
                else:
                    current = hash_file(f)
                    expected = baseline.get(category, {}).get(f)
                    if expected and current != expected:
                        mismatches.append((f, expected, current))
    if mismatches:
        log("[!] Hash mismatches detected:")
        for f, exp, cur in mismatches:
            log(f" - {f}: expected {exp}, got {cur}")
    else:
        log("All mandatory files match baseline.")