import os
import json
from .usb import SETTINGS_FILE


with open(SETTINGS_FILE) as f:
    settings = json.load(f)

USB_MOUNT = settings["USB_MOUNT"]
BASELINE_HASH_FILE = os.path.join(USB_MOUNT, "baseline_hashes.json")
BACKUP_DIR = "/tmp/backups"
GPG_HOME = "/home/harpoon/.gnupg"
TRUSTED_KEY = "CDED 9917 B36D 9263 857B FC51 72E6 8FAE A13F 0903"  # Change this
KEEPASS_DB = os.path.join(USB_MOUNT, "vault.kdbx")
KEEPASS_PASS_FILE = os.path.join(USB_MOUNT, "vault_pass.gpg")
EXPECTED_PORT = settings.get("EXPECTED_PORT")

def update_settings(new_settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(new_settings, f, indent=2)

def log(msg):
    print(f"[+] {msg}")

def get_mandatory_files():
    # Return your mandatory files dictionary here
    return {
        "DOCS": ["/etc/passwd", "/etc/shadow"],
        "NETWORKING": ["/etc/hosts", "/etc/hostname", "/etc/resolv.conf", "/etc/fstab", "/etc/NetworkManager/NetworkManager.conf"],
        "MISC": ["/etc/ssh/sshd_config"],
        "LOGS": []
    }

