import os
import subprocess
import time
import pyudev # type: ignore
import shutil
import gnupg # type: ignore
import hashlib
import json
from pykeepass import create_database, PyKeePass # pyright: ignore[reportMissingImports]
from .config import (
    BACKUP_DIR,
    GPG_HOME,
    TRUSTED_KEY,
    get_mandatory_files,
    log,
    SETTINGS_FILE
)
from .config import get_usb_mount, get_expected_port, get_baseline_hash_file, get_keepass_db
from .hashing import hash_file, generate_baseline, compare_with_baseline
from .usb import select_usb_port, select_usb_mount, save_selected_settings
from .scheduler import periodic_hash_check

# Quick-access programs when trusted USB is plugged in
SECURITY_PROGRAMS = [
    ["keepassxc", get_keepass_db],
    ["firefox", "https://localhost:9090"],  # Cockpit web UI
    ["wireshark"]
]

IMPORT_DIRS = {
    "DOCS": "/home/harpoon/important/DOCS",
    "NETWORKING": "/home/harpoon/important/NETWORKING",
    "SCREENSHOTS": "/home/harpoon/important/SCREENSHOTS",
    "MISC": "/home/harpoon/important/MISC"
}


EXPECTED_PORT = "5-9"  # Correct USB port ID
# ----------------------------

gpg = gnupg.GPG(homedir=GPG_HOME)

def log(msg):
    print(f"[+] {msg}")

# --- GPG Validation ---
def verify_usb_trust():
    pubkey_file = os.path.join(get_usb_mount, "trusted_pubkey.asc")
    if not os.path.exists(pubkey_file):
        log("No trusted GPG key found on USB.")
        return False
    with open(pubkey_file, "rb") as f:
        import_result = gpg.import_keys(f.read())
    if TRUSTED_KEY in str(import_result.fingerprints):
        log("USB device verified with GPG trust.")
        return True
    return False

# --- Backup & Encryption with Enhanced Drama ---
def backup_files():
    log("🔥 THE HAMMER'S PROTECTIVE POWER AWAKENS! 🔥")
    time.sleep(1)
    log("⚡ Gathering sacred artifacts from across the Nine Realms...")
    
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    temp_dir = os.path.join(BACKUP_DIR, f"session_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)
    
    log(f"🏛️  Creating divine vault: {temp_dir}")
    time.sleep(0.5)

    # Copy all import dirs with dramatic progress
    for name, d in IMPORT_DIRS.items():
        if os.path.exists(d):
            log(f"📦 Protecting realm: {name} from {d}")
            time.sleep(0.3)  # Pause for dramatic effect
            shutil.copytree(d, os.path.join(temp_dir, name), dirs_exist_ok=True)
            log(f"✅ Realm {name} secured in the divine vault")

    # Copy mandatory files into respective dirs with suspense
    log("🔍 Securing mandatory treasures...")
    for category, files in get_mandatory_files().items():
        category_dir = os.path.join(temp_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        log(f"📂 Processing {category} artifacts...")
        for i, f in enumerate(files):
            if os.path.exists(f):
                file_hash = hash_file(f)
                log(f"🔒 Securing {f}")
                log(f"   📜 Divine signature: {file_hash}")
                
                dest = os.path.join(category_dir, os.path.basename(f))
                try:
                    if os.path.isdir(f):
                        shutil.copytree(f, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(f, dest)
                    log(f"   ✨ Artifact preserved with Thor's blessing")
                except PermissionError:
                    log(f"   🚫 Artifact {f} resisted protection (insufficient permissions)")
                
                # Small delay between files for suspense
                if i % 3 == 0:  # Pause every 3 files
                    time.sleep(0.2)

    # Compare to baseline before archiving with drama
    log("🔮 Consulting the ancient baseline prophecies...")
    time.sleep(1)
    compare_with_baseline()

    # Create archive with ceremonial flair
    archive_name = os.path.join(BACKUP_DIR, f"important_{timestamp}.tar.gz")
    log("📦 Forging the sacred archive...")
    log("⚡ Compressing realms with divine power...")
    time.sleep(1.5)
    shutil.make_archive(archive_name.replace(".tar.gz", ""), "gztar", temp_dir)
    log(f"✅ Archive forged: {archive_name}")

    log("🔐 Invoking GPG encryption ritual...")
    time.sleep(1)
    with open(archive_name, "rb") as f:
        encrypted_result = gpg.encrypt_file(f, recipients=[TRUSTED_KEY], output=archive_name + ".gpg")
    
    if encrypted_result.ok:
        log(f"⚡ DIVINE ENCRYPTION COMPLETE! ⚡")
        log(f"🛡️  Protected archive: {archive_name}.gpg")
    else:
        log(f"💥 Encryption ritual failed: {encrypted_result.status}")
    
    time.sleep(0.5)
    return archive_name + ".gpg"

# --- KeePass + Security Tools Launcher with Drama ---
def launch_security_suite():
    log("⚡ SUMMONING THE GUARDIANS OF ASGARD! ⚡")
    time.sleep(1)
    log("🛡️  Awakening the sacred security arsenal...")
    
    try:
        security_tools = [
            ("🔐 KeePassXC", ["keepassxc", get_keepass_db]),
            ("🌐 Cockpit Command Center", ["firefox", "https://localhost:9090"]),
            ("🔍 Wireshark Network Sentinel", ["wireshark"])
        ]
        
        for tool_name, prog in security_tools:
            log(f"⚡ Summoning {tool_name}...")
            time.sleep(0.8)
            try:
                subprocess.Popen(prog, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log(f"✅ {tool_name} stands ready for battle!")
            except FileNotFoundError:
                log(f"⚠️  {tool_name} could not be summoned (not installed)")
        
        time.sleep(1)
        log("🎆 THE SECURITY COUNCIL IS ASSEMBLED! 🎆")
        log("⚡ All guardians stand ready to defend the realm!")
        
    except Exception as e:
        log(f"💥 Error summoning the guardians: {e}")
        log("🔥 Some tools of war remain dormant!")

# --- USB Disconnect with Ceremonial Farewell ---
def disconnect_usb(device_node):
    log("🌪️  Preparing to banish the unauthorized presence...")
    time.sleep(1)
    log(f"📤 Unmounting {device_node} from the sacred realm...")
    
    try:
        subprocess.run(["sudo", "umount", device_node], check=True)
        log("✅ Device successfully unmounted from the realm")
    except subprocess.CalledProcessError:
        log("⚠️  Device resisted unmounting - proceeding with force")
    
    time.sleep(0.5)
    log(f"⚡ Ejecting {device_node} back to the void...")
    
    try:
        subprocess.run(["sudo", "eject", device_node], check=True)
        log("🚀 Device banished! The realm is purified!")
    except subprocess.CalledProcessError:
        log("💥 Ejection incomplete - manual intervention may be required")
    
    time.sleep(0.5)
    log("🛡️  The sacred ports return to their vigilant watch...")

# --- Main USB Event Loop with Enhanced Drama ---
def monitor_usb():
    from .effects import mjolnir_startup_sequence, lockdown_alarm_sequence, dramatic_countdown_with_effects
    
    # Dramatic startup
    mjolnir_startup_sequence()
    time.sleep(1)
    
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")
    
    log("🔍 MJOLNIR's eternal vigil begins...")
    log("⚡ Scanning all Nine Realms for intruders...")

    for device in monitor:
        if device.action == "add":
            device_node = device.device_node
            device_port = device.get("DEVPATH", "")

            log("🌩️  DISTURBANCE DETECTED IN THE REALMS!")
            time.sleep(0.5)
            log(f"📍 Investigating: {device_node} at realm {device_port}")
            
            # Dramatic analysis pause
            log("🔍 Analyzing threat level...")
            time.sleep(1.5)
            log("⚡ Checking divine authorization...")
            time.sleep(1)

            if EXPECTED_PORT not in device_port:
                lockdown_alarm_sequence()
                log("💀 UNAUTHORIZED VESSEL DETECTED!")
                time.sleep(1)
                log("🔥 Initiating protective measures...")
                
                # Dramatic countdown before action
                dramatic_countdown_with_effects(5, "SECURITY PROTOCOL ACTIVATION IN")
                time.sleep(6)  # Wait for countdown to complete

                if verify_usb_trust():
                    log("✨ GPG signature verified - Trusted artifact detected")
                    log("🛡️  Proceeding with sacred backup ritual...")
                    time.sleep(1)
                    
                    compare_with_baseline()
                    encrypted_archive = backup_files()
                    shutil.copy(encrypted_archive, get_usb_mount)
                    launch_security_suite()
                    
                    log("⚡ DIVINE PROTECTION COMPLETE!")
                else:
                    log("💥 UNTRUSTED ARTIFACT! MJOLNIR REJECTS THIS VESSEL!")
                    log("🚫 Backup denied - The unworthy shall not pass!")

                log("🔨 Banishing the unauthorized presence...")
                disconnect_usb(device_node)
                log("✅ Realm secured. Returning to eternal watch.")
            else:
                log("🎉 REJOICE! THE CHOSEN VESSEL RETURNS!")
                time.sleep(0.5)
                log("⚡ Sacred port recognized - Divine blessing confirmed")
                log("🛡️  No action required. The worthy are welcome.")

if __name__ == "__main__":
    print("🔨" + "=" * 58 + "🔨")
    print("⚡" + " " * 20 + "MJOLNIR INITIALIZATION" + " " * 20 + "⚡")
    print("🔨" + "=" * 58 + "🔨")
    time.sleep(1)
    
    log("🌟 Beginning sacred configuration ritual...")
    selected_port = select_usb_port()
    selected_mount = select_usb_mount()
    save_selected_settings(selected_port, selected_mount)
    
    log("🔮 Generating divine protection baseline...")
    generate_baseline()
    compare_with_baseline()
    
    log("📅 Initializing temporal guardianship...")
    periodic_hash_check()
    
    log("🛡️  All preparations complete. MJOLNIR stands ready!")
    time.sleep(1)
    
    monitor_usb()