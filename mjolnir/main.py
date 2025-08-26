import os
import subprocess
import time
import pyudev
import shutil
import gnupg
import hashlib
import json
from pykeepass import create_database, PyKeePass

# ----------------------------
# CONFIG
# ----------------------------
BACKUP_DIR = "/tmp/backups"
USB_MOUNT = "/media/usb"
GPG_HOME = "/home/youruser/.gnupg"
TRUSTED_KEY = "YOUR_GPG_KEY_FINGERPRINT"  # Change this
KEEPASS_DB = os.path.join(USB_MOUNT, "vault.kdbx")
KEEPASS_PASS_FILE = os.path.join(USB_MOUNT, "vault_pass.gpg")
BASELINE_HASH_FILE = os.path.join(USB_MOUNT, "baseline_hashes.json")

# Quick-access programs when trusted USB is plugged in
SECURITY_PROGRAMS = [
    ["keepassxc", KEEPASS_DB],
    ["firefox", "https://localhost:9090"],  # Cockpit web UI
    ["wireshark"]
]

IMPORT_DIRS = {
    "DOCS": "/home/harpoon/important/DOCS",
    "NETWORKING": "/home/harpoon/important/NETWORKING",
    "SCREENSHOTS": "/home/harpoon/important/SCREENSHOTS",
    "MISC": "/home/harpoon/important/MISC"
}

# Mandatory files organized by category
def get_mandatory_files():
    return {
        "DOCS": ["/etc/passwd", "/etc/shadow"],
        "NETWORKING": [
            "/etc/hosts",
            "/etc/hostname",
            "/etc/resolv.conf",
            "/etc/fstab",
            "/etc/network/interfaces",
            "/etc/NetworkManager/",
            "/etc/openvpn/",
            "/etc/squid/",
            "/etc/ufw/",
            "/etc/iptables/"
        ],
        "MISC": [
            "/etc/ssh/sshd_config"
        ],
        "LOGS": [
            "/var/log/auth.log",
            "/var/log/syslog",
            "/var/log/dmesg",
            "/var/log/kern.log"
        ]
    }

EXPECTED_PORT = "1-1"  # Correct USB port ID
# ----------------------------

gpg = gnupg.GPG(homedir=GPG_HOME)

def log(msg):
    print(f"[+] {msg}")

# --- Hashing ---
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

# Generate baseline hash list for mandatory files + dirs
def generate_baseline():
    hashes = {}
    for category, files in get_mandatory_files().items():
        hashes[category] = {}
        for f in files:
            if os.path.exists(f):
                if os.path.isdir(f):
                    # Hash each file in dir
                    for root, _, filenames in os.walk(f):
                        for fn in filenames:
                            path = os.path.join(root, fn)
                            hashes[category][path] = hash_file(path)
                else:
                    hashes[category][f] = hash_file(f)
    with open(BASELINE_HASH_FILE, "w") as bf:
        json.dump(hashes, bf, indent=2)
    log(f"Baseline hashes written to {BASELINE_HASH_FILE}")

# Compare current hashes with baseline
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

# --- GPG Validation ---
def verify_usb_trust():
    pubkey_file = os.path.join(USB_MOUNT, "trusted_pubkey.asc")
    if not os.path.exists(pubkey_file):
        log("No trusted GPG key found on USB.")
        return False
    with open(pubkey_file, "rb") as f:
        import_result = gpg.import_keys(f.read())
    if TRUSTED_KEY in str(import_result.fingerprints):
        log("USB device verified with GPG trust.")
        return True
    return False

# --- Backup & Encryption ---
def backup_files():
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    temp_dir = os.path.join(BACKUP_DIR, f"session_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)

    # Copy all import dirs
    for name, d in IMPORT_DIRS.items():
        if os.path.exists(d):
            log(f"Adding directory {d} to backup.")
            shutil.copytree(d, os.path.join(temp_dir, name), dirs_exist_ok=True)

    # Copy mandatory files into respective dirs
    for category, files in get_mandatory_files().items():
        category_dir = os.path.join(temp_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        for f in files:
            if os.path.exists(f):
                file_hash = hash_file(f)
                log(f"Including {f} [sha256: {file_hash}]")
                dest = os.path.join(category_dir, os.path.basename(f))
                try:
                    if os.path.isdir(f):
                        shutil.copytree(f, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(f, dest)
                except PermissionError:
                    log(f"[!] Skipped {f}, insufficient permissions.")

    # Compare to baseline before archiving
    compare_with_baseline()

    # Create archive
    archive_name = os.path.join(BACKUP_DIR, f"important_{timestamp}.tar.gz")
    shutil.make_archive(archive_name.replace(".tar.gz", ""), "gztar", temp_dir)

    log(f"Encrypting archive with GPG -> {archive_name}.gpg")
    with open(archive_name, "rb") as f:
        gpg.encrypt_file(f, recipients=[TRUSTED_KEY], output=archive_name + ".gpg")
    return archive_name + ".gpg"

# --- KeePass + Security Tools Launcher ---
def launch_security_suite():
    try:
        for prog in SECURITY_PROGRAMS:
            subprocess.Popen(prog)
        log("Security suite launched: KeePass, Cockpit, Wireshark.")
    except Exception as e:
        log(f"[!] Error launching security suite: {e}")

# --- USB Disconnect ---
def disconnect_usb(device_node):
    log(f"Unmounting and ejecting {device_node}")
    subprocess.run(["sudo", "umount", device_node])
    subprocess.run(["sudo", "eject", device_node])

# --- Main USB Event Loop ---
def monitor_usb():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")

    for device in monitor:
        if device.action == "add":
            device_node = device.device_node
            device_port = device.get("DEVPATH", "")

            log(f"USB device plugged in: {device_node} at {device_port}")

            if EXPECTED_PORT not in device_port:
                log("Device in wrong port → backup trigger.")

                if verify_usb_trust():
                    compare_with_baseline()
                    encrypted_archive = backup_files()
                    shutil.copy(encrypted_archive, USB_MOUNT)
                    launch_security_suite()
                else:
                    log("Untrusted USB device. Skipping backup.")

                disconnect_usb(device_node)
            else:
                log("Device in correct port. No action taken.")

if __name__ == "__main__":
    monitor_usb()
