import os
import hashlib
import json
from collections import OrderedDict
from .config import get_baseline_hash_file, get_mandatory_files, log

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
    with open(get_baseline_hash_file(), "w") as bf:
        json.dump(hashes, bf, indent=2)
    log(f"Baseline hashes written to {get_baseline_hash_file()}")

def compare_with_baseline():
    if not os.path.exists(get_baseline_hash_file()):
        log("[!] No baseline hash file found.")
        return

    with open(get_baseline_hash_file(), "r") as bf:
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

def generate_consolidated_hash():
    """Generate a consolidated hash from all file hashes for easy verification."""
    if not os.path.exists(get_baseline_hash_file()):
        log("[!] No baseline hash file found. Generate baseline first.")
        return None

    with open(get_baseline_hash_file(), "r") as bf:
        baseline = json.load(bf)

    # Create ordered list of all file hashes
    all_hashes = []
    for category in sorted(baseline.keys()):
        for filepath in sorted(baseline[category].keys()):
            file_hash = baseline[category][filepath]
            if file_hash:  # Only include valid hashes
                all_hashes.append(f"{filepath}:{file_hash}")
    
    # Create master hash from all file hashes
    master_hash_data = "\n".join(all_hashes)
    master_hash = hashlib.sha256(master_hash_data.encode()).hexdigest()
    
    return {
        "master_hash": master_hash,
        "file_count": len(all_hashes),
        "hash_list": all_hashes
    }

def save_consolidated_hash():
    """Save consolidated hash information to the USB device."""
    consolidated = generate_consolidated_hash()
    if not consolidated:
        return None
    
    try:
        from .config import get_usb_mount
        usb_mount = get_usb_mount()
        if not usb_mount:
            log("[!] USB mount not configured.")
            return None
            
        consolidated_file = os.path.join(usb_mount, "consolidated_hashes.json")
        with open(consolidated_file, "w") as f:
            json.dump(consolidated, f, indent=2)
        
        log(f"Consolidated hash saved to {consolidated_file}")
        log(f"Master hash: {consolidated['master_hash']}")
        log(f"Files included: {consolidated['file_count']}")
        
        return consolidated_file
    except Exception as e:
        log(f"[!] Error saving consolidated hash: {e}")
        return None

def verify_consolidated_hash():
    """Verify current files against stored consolidated hash."""
    try:
        from .config import get_usb_mount
        usb_mount = get_usb_mount()
        if not usb_mount:
            log("[!] USB mount not configured.")
            return False
            
        consolidated_file = os.path.join(usb_mount, "consolidated_hashes.json")
        if not os.path.exists(consolidated_file):
            log("[!] No consolidated hash file found.")
            return False
        
        with open(consolidated_file, "r") as f:
            stored_consolidated = json.load(f)
        
        # Generate current consolidated hash
        current_consolidated = generate_consolidated_hash()
        if not current_consolidated:
            return False
        
        # Compare master hashes
        stored_master = stored_consolidated.get("master_hash")
        current_master = current_consolidated["master_hash"]
        
        if stored_master == current_master:
            log("✓ Consolidated hash verification PASSED")
            log(f"Master hash: {current_master}")
            log(f"Files verified: {current_consolidated['file_count']}")
            return True
        else:
            log("[!] Consolidated hash verification FAILED")
            log(f"Expected: {stored_master}")
            log(f"Current:  {current_master}")
            
            # Show detailed differences
            stored_hashes = set(stored_consolidated.get("hash_list", []))
            current_hashes = set(current_consolidated["hash_list"])
            
            missing = stored_hashes - current_hashes
            added = current_hashes - stored_hashes
            
            if missing:
                log("[!] Missing file hashes:")
                for item in sorted(missing):
                    log(f"  - {item}")
            
            if added:
                log("[!] New file hashes:")
                for item in sorted(added):
                    log(f"  + {item}")
            
            return False
            
    except Exception as e:
        log(f"[!] Error during consolidated hash verification: {e}")
        return False

def get_hash_summary():
    """Get a human-readable summary of current hash status."""
    summary = {
        "baseline_exists": os.path.exists(get_baseline_hash_file()),
        "file_count": 0,
        "categories": {},
        "consolidated_hash": None,
        "last_updated": None
    }
    
    if summary["baseline_exists"]:
        try:
            with open(get_baseline_hash_file(), "r") as bf:
                baseline = json.load(bf)
            
            for category, files in baseline.items():
                summary["categories"][category] = len(files)
                summary["file_count"] += len(files)
            
            # Get file modification time
            summary["last_updated"] = os.path.getmtime(get_baseline_hash_file())
            
            # Get consolidated hash if available
            consolidated = generate_consolidated_hash()
            if consolidated:
                summary["consolidated_hash"] = consolidated["master_hash"]
                
        except Exception as e:
            log(f"[!] Error reading hash summary: {e}")
    
    return summary