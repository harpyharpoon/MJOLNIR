import nfc
import threading
import time
import sys

AUTHORIZED_IDS = ["04A2243B993580", "123456ABCD9876"]  # Example NFC tag UIDs

def dramatic_print(message, delay=0.05):
    """Print message character by character for dramatic effect."""
    for char in message:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def countdown_warning(seconds, message_prefix=""):
    """Display a dramatic countdown with escalating urgency."""
    for i in range(seconds, 0, -1):
        if i <= 5:
            dramatic_print(f"🔥 {message_prefix} {i} seconds remaining! 🔥", delay=0.03)
        elif i <= 10:
            dramatic_print(f"⚡ {message_prefix} {i} seconds remaining... ⚡", delay=0.04)
        else:
            print(f"⏰ {message_prefix} {i} seconds remaining...")
        time.sleep(1)

def on_connect(tag):
    dramatic_print("⚡ MJOLNIR DETECTS PRESENCE... ⚡")
    time.sleep(0.5)
    tag_id = tag.identifier.hex().upper()
    dramatic_print(f"🔍 Analyzing authentication signature: {tag_id}")
    time.sleep(1)
    return tag_id

def wait_for_nfc_tap(timeout=30):
    dramatic_print("🛡️  MJOLNIR'S GUARDIAN PROTOCOL ACTIVATED 🛡️")
    time.sleep(1)
    dramatic_print("⚡ Seeking the worthy... Present your key to prove your identity ⚡")
    time.sleep(0.5)
    
    clf = nfc.ContactlessFrontend('usb')
    tag_id = None
    start_time = time.time()
    
    def worker():
        nonlocal tag_id
        tag = clf.connect(rdwr={'on-connect': on_connect})
        if tag:
            tag_id = tag.identifier.hex().upper()
    
    t = threading.Thread(target=worker)
    t.start()
    
    # Dramatic countdown with escalating warnings
    elapsed = 0
    while elapsed < timeout and tag_id is None:
        remaining = timeout - elapsed
        if remaining <= 10:
            countdown_warning(min(int(remaining), 10), "CRITICAL:")
            break
        elif remaining <= 20:
            dramatic_print(f"⚠️  Time grows short... {int(remaining)} seconds remain ⚠️")
        else:
            print(f"🕐 {int(remaining)} seconds to prove worthiness...")
        
        time.sleep(5)
        elapsed = time.time() - start_time
    
    t.join(timeout)
    clf.close()
    return tag_id

def execute_lockdown():
    """Dramatic lockdown sequence with mythological flair."""
    dramatic_print("🔨 MJOLNIR'S WRATH AWAKENS! 🔨", delay=0.08)
    time.sleep(1)
    dramatic_print("⚡ INITIATING ASGARDIAN SECURITY PROTOCOL ⚡", delay=0.06)
    time.sleep(1)
    dramatic_print("🛡️  All realms shall be protected... 🛡️", delay=0.04)
    time.sleep(2)
    # Add actual lockdown functionality here
    dramatic_print("✅ LOCKDOWN COMPLETE - THE REALM IS SECURE ✅")

if __name__ == "__main__":
    dramatic_print("🔨 MJOLNIR SECURITY SYSTEM INITIALIZED 🔨", delay=0.08)
    time.sleep(1)
    dramatic_print("⚡ Only the worthy may command Thor's hammer... ⚡")
    time.sleep(1)
    
    nfc_id = wait_for_nfc_tap(timeout=30)
    if nfc_id:
        dramatic_print(f"✨ Identity confirmed: {nfc_id} ✨")
        time.sleep(1)
        if nfc_id in AUTHORIZED_IDS:
            dramatic_print("🎉 WORTHY! You have been deemed fit to wield MJOLNIR! 🎉", delay=0.06)
            time.sleep(1)
            dramatic_print("⚡ Access granted. The power of Thor flows through you... ⚡")
            # execute_lockdown()
        else:
            dramatic_print("🚫 UNWORTHY! This key holds no power here! 🚫", delay=0.04)
            time.sleep(1)
            dramatic_print("⚡ MJOLNIR REJECTS YOUR PRESENCE ⚡", delay=0.06)
    else:
        dramatic_print("💀 SILENCE... The worthy have not answered the call 💀", delay=0.05)
        time.sleep(1)
        dramatic_print("🔥 MJOLNIR'S PATIENCE HAS ENDED 🔥", delay=0.06)

def usb_plugged_in_wrong_port():
    """Placeholder function - should be implemented elsewhere."""
    return False

if usb_plugged_in_wrong_port():
    dramatic_print("🚨 THREAT DETECTED! MJOLNIR SENSES DECEPTION! 🚨", delay=0.04)
    time.sleep(1)
    dramatic_print("⚠️  An unauthorized presence dares to approach... ⚠️")
    time.sleep(1)
    dramatic_print("🔥 Present your key within 30 seconds or face MJOLNIR'S JUDGMENT! 🔥", delay=0.05)

    nfc_id = wait_for_nfc_tap(timeout=30)
    
    if nfc_id and nfc_id in AUTHORIZED_IDS:
        dramatic_print("⚡ MJOLNIR RECOGNIZES THE WORTHY ⚡", delay=0.06)
        time.sleep(1)
        dramatic_print("🔨 Proceeding with righteous lockdown... 🔨")
        execute_lockdown()
    else:
        dramatic_print("💥 THE HAMMER'S WRATH IS UNLEASHED! 💥", delay=0.05)
        time.sleep(1)
        dramatic_print("🔥 Authentication failed! MJOLNIR's fury knows no bounds! 🔥", delay=0.04)
        # log_event("Failed NFC auth on trigger port event.")
        dramatic_print("⚡ Emergency protocols activated - The realm must be protected! ⚡")
