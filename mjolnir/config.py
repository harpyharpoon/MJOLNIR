import os
import json
from .usb import SETTINGS_FILE


with open(SETTINGS_FILE) as f:
    settings = json.load(f)

BACKUP_DIR = "/tmp/backups"
GPG_HOME = "/home/harpoon/.gnupg"
TRUSTED_KEY = "CDED 9917 B36D 9263 857B FC51 72E6 8FAE A13F 0903"  # Change this

def get_settings():
    with open(SETTINGS_FILE) as f:
        return json.load(f)

def get_usb_mount():
    return get_settings().get("USB_MOUNT")

def get_expected_port():
    return get_settings().get("EXPECTED_PORT")

def get_baseline_hash_file():
    usb_mount = get_usb_mount()
    if not usb_mount:
        raise ValueError("USB_MOUNT is not set in settings.json")
    return os.path.join(get_usb_mount, "baseline_hashes.json")

def get_keepass_db():
    usb_mount = get_usb_mount()
    if not usb_mount:
        raise ValueError("USB_MOUNT is not set in settings.json")
    return os.path.join(usb_mount, "vault.kdbx")

def get_keepass_pass_file():
    usb_mount = get_usb_mount()
    if not usb_mount:
        raise ValueError("USB_MOUNT is not set in settings.json")
    return os.path.join(usb_mount, "vault_pass.gpg")

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

def get_baseline_hash_file():
    settings = get_settings()
    usb_mount = settings["USB_MOUNT"]
    return os.path.join(usb_mount, "baseline_hashes.json")

def get_settings():
    return settings

def get_hash_rotation_days():
    return get_settings().get('HASH_ROTATION_DAYS', 7) # Default is 7 days



