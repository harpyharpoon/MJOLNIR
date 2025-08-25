import nfc
import threading

AUTHORIZED_IDS = ["04A2243B993580", "123456ABCD9876"]  # Example NFC tag UIDs

def on_connect(tag):
    print(f"NFC tag detected: {tag.identifier.hex().upper()}")
    return tag.identifier.hex().upper()

def wait_for_nfc_tap(timeout=30):
    clf = nfc.ContactlessFrontend('usb')
    tag_id = None
    def worker():
        nonlocal tag_id
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        if tag:
            tag_id = tag.identifier.hex().upper()
    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout)
    clf.close()
    return tag_id

if __name__ == "__main__":
    print("Tap your NFC security key...")
    nfc_id = wait_for_nfc_tap(timeout=30)
    if nfc_id:
        print(f"NFC Key: {nfc_id}")
        if nfc_id in AUTHORIZED_IDS:
            print("Access granted. Proceeding.")
            # execute_lockdown()
        else:
            print("Unauthorized NFC key!")
    else:
        print("No NFC key detected within timeout.")