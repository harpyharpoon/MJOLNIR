import pyudev
import threading
from .config import get_expected_port, log

def monitor_usb_events(status_callback=None):
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

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