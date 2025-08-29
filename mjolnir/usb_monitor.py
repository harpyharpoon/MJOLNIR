import pyudev
import threading
import time
import sys
from .config import get_expected_port, log

def dramatic_log(message, delay=0.03):
    """Enhanced logging with dramatic character-by-character printing."""
    timestamp = time.strftime("%H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    
    for char in full_message:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def mjolnir_log(message, urgency="normal"):
    """MJOLNIR-themed logging with different urgency levels."""
    if urgency == "critical":
        dramatic_log(f"🔥 MJOLNIR CRITICAL: {message} 🔥", delay=0.02)
    elif urgency == "warning":
        dramatic_log(f"⚡ MJOLNIR ALERT: {message} ⚡", delay=0.025)
    elif urgency == "success":
        dramatic_log(f"✨ MJOLNIR BLESSED: {message} ✨", delay=0.035)
    else:
        dramatic_log(f"🛡️  MJOLNIR: {message}")

def detection_sequence(device_type, port):
    """Dramatic detection sequence for USB devices."""
    mjolnir_log("Scanning the Nine Realms for intruders...", "normal")
    time.sleep(0.8)
    mjolnir_log(f"⚡ Presence detected in realm sector: {port} ⚡", "warning")
    time.sleep(0.5)
    mjolnir_log("🔍 Analyzing threat level and divine authorization...", "normal")
    time.sleep(1.2)
    
    for i in range(3):
        dramatic_log(".", delay=0.5)
        time.sleep(0.3)
    
    return device_type

def check_usb_device_at_startup(status_callback=None):
    """Check if the trusted USB device is already connected at startup."""
    mjolnir_log("🔨 MJOLNIR AWAKENS 🔨", "success")
    time.sleep(0.5)
    mjolnir_log("Scanning for trusted artifacts at system genesis...", "normal")
    time.sleep(1)
    
    try:
        context = pyudev.Context()
        expected_port = get_expected_port()
        
        if not expected_port:
            mjolnir_log("⚠️  No sacred port has been consecrated", "warning")
            if status_callback:
                status_callback(False)
            return False
        
        mjolnir_log(f"🔍 Seeking the chosen vessel in realm: {expected_port}", "normal")
        time.sleep(1)
        
        # Check all USB devices
        device_count = 0
        for device in context.list_devices(subsystem='usb', DEVTYPE='usb_device'):
            device_count += 1
            port = device.device_path.split('/')[-1]
            if port == expected_port:
                mjolnir_log("⚡ THE CHOSEN ONE STIRS! ⚡", "success")
                time.sleep(0.5)
                mjolnir_log(f"✨ Trusted artifact found in sacred port {port}! ✨", "success")
                time.sleep(0.5)
                mjolnir_log("🛡️  Divine protection is already active", "success")
                if status_callback:
                    status_callback(True)
                return True
        
        mjolnir_log(f"🌫️  Searched {device_count} realms... The chosen one slumbers", "normal")
        time.sleep(0.5)
        mjolnir_log("⏳ MJOLNIR awaits the return of its master...", "warning")
        if status_callback:
            status_callback(False)
        return False
        
    except Exception as e:
        mjolnir_log(f"💥 The realms trembled! Error in divine sight: {e}", "critical")
        if status_callback:
            status_callback(False)
        return False

def monitor_usb_events(status_callback=None):
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    # First check if device is already connected
    check_usb_device_at_startup(status_callback)
    
    mjolnir_log("🔍 MJOLNIR'S ETERNAL VIGIL BEGINS 🔍", "success")
    time.sleep(1)
    mjolnir_log("⚡ Watching all Nine Realms for the chosen artifact... ⚡", "normal")
    time.sleep(0.5)
    
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            mjolnir_log("🌩️  DISTURBANCE IN THE REALMS! 🌩️", "warning")
            time.sleep(0.3)
            
            port = device.device_path.split('/')[-1]
            expected_port = get_expected_port()
            
            device_result = detection_sequence("artifact", port)
            
            if port == expected_port:
                mjolnir_log("🎆 REJOICE! THE WORTHY HAVE RETURNED! 🎆", "success")
                time.sleep(0.5)
                mjolnir_log(f"⚡ The sacred port {port} welcomes its master! ⚡", "success")
                time.sleep(0.5)
                mjolnir_log("🛡️  Divine protection flows through the realm once more", "success")
                if status_callback:
                    status_callback(True)
            else:
                mjolnir_log("🚨 TREACHERY DETECTED! 🚨", "critical")
                time.sleep(0.5)
                mjolnir_log(f"💀 An UNWORTHY vessel dares approach realm {port}! 💀", "critical")
                time.sleep(0.5)
                mjolnir_log("⚡ MJOLNIR'S WRATH STIRS... PREPARE FOR JUDGMENT! ⚡", "critical")
                time.sleep(1)
                mjolnir_log("🔥 SECURITY PROTOCOLS ACTIVATING 🔥", "critical")
                if status_callback:
                    status_callback(False)
                    
        elif device.action == 'remove':
            mjolnir_log("🌪️  A presence fades from the realm...", "warning")
            time.sleep(0.5)
            mjolnir_log("😔 The chosen one has departed... MJOLNIR weeps", "warning")
            time.sleep(0.5)
            mjolnir_log("⏳ Returning to eternal watch... Awaiting the worthy", "normal")
            if status_callback:
                status_callback(False)

if __name__ == "__main__":
    monitor_usb_events()