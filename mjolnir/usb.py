import tkinter as tk
from tkinter import simpledialog, messagebox
import pyudev
import os
import json

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings():
    with open(SETTINGS_FILE) as f:
        return json.load(f)

settings = load_settings()
USB_MOUNT = settings["USB_MOUNT"]
EXPECTED_PORT = settings["EXPECTED_PORT"]

def list_usb_ports():
    context = pyudev.Context()
    ports = []
    for device in context.list_devices(subsystem='usb', DEVTYPE='usb_device'):
        port = device.device_path.split('/')[-1]
        desc = f"{device.get('ID_MODEL', 'Unknown')} ({port})"
        ports.append((desc, port))
    return ports

def select_usb_port():
    ports = list_usb_ports()
    if not ports:
        messagebox.showerror("No USB Devices", "No USB devices found.")
        return None

    root = tk.Tk()
    root.withdraw()
    port_names = [desc for desc, port in ports]
    selected = simpledialog.askstring("Select USB Port", "Available USB Devices:\n" + "\n".join(port_names))
    for desc, port in ports:
        if selected and selected in desc:
            return port
    return None

def save_selected_port(selected_port, usb_mount):
    settings = {
        "USB_MOUNT": usb_mount,
        "EXPECTED_PORT": selected_port
    }
    
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

if __name__ == "__main__":
    port = select_usb_port()
    if port:
        print(f"Selected port: {port}")
        save_selected_port(port, USB_MOUNT)

        print("USB port selection saved.")
    else:
        print("No port selected.")