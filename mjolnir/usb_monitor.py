import pyudev
import threading
from .config import get_expected_port, log

def check_usb_device_at_startup(status_callback=None):
    """Check if the trusted USB device is already connected at startup."""
    try:
        context = pyudev.Context()
        expected_port = get_expected_port()
        
        if not expected_port:
            log("No expected port configured.")
            if status_callback:
                status_callback(False)
            return False
        
        # Check all USB devices
        for device in context.list_devices(subsystem='usb', DEVTYPE='usb_device'):
            port = device.device_path.split('/')[-1]
            if port == expected_port:
                log(f"Trusted USB device found on port {port} at startup!")
                if status_callback:
                    status_callback(True)
                return True
        
        log("No trusted USB device found at startup.")
        if status_callback:
            status_callback(False)
        return False
        
    except Exception as e:
        log(f"Error checking USB devices at startup: {e}")
        if status_callback:
            status_callback(False)
        return False

def monitor_usb_events(status_callback=None):
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    # First check if device is already connected
    check_usb_device_at_startup(status_callback)

    log("Monitoring for trusted USB device...")
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            port = device.device_path.split('/')[-1]
            expected_port = get_expected_port()
            if port == expected_port:
                log(f"Trusted USB device connected on port {port}!")
                if status_callback:
                    status_callback(True)
            else:
                log(f"Untrusted USB device connected on port {port}.")
                if status_callback:
                    status_callback(False)
        elif device.action == 'remove':
            log("A USB device was removed.")
            if status_callback:
                status_callback(False)

if __name__ == "__main__":
    monitor_usb_events()