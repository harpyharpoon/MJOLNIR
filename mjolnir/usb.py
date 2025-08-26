import tkinter as tk
from tkinter import simpledialog, messagebox
import pyudev # pyright: ignore[reportMissingImports]
import os
import json

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

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
    selected = simpledialog.askstring(
        "Select USB Port",
        "Available USB Devices:\n" + "\n".join(port_names) + "\n\nType part of the device name to select."
    )
    for desc, port in ports:
        if selected and selected in desc:
            return port
    return None

def list_usb_mounts():
    # Adjust base path for your username if needed
    base = "/run/media/" + os.getlogin()
    if not os.path.exists(base):
        return []
    return [os.path.join(base, d) for d in os.listdir(base) if os.path.ismount(os.path.join(base, d))]

def select_usb_mount():
    mounts = list_usb_mounts()
    if not mounts:
        messagebox.showerror("No USB Mounts", "No USB mount points found.")
        return None

    root = tk.Tk()
    root.withdraw()
    mount = simpledialog.askstring(
        "Select USB Mount",
        "Available USB Mounts:\n" + "\n".join(mounts) + "\n\nType or paste the full path to select."
    )
    if mount in mounts:
        return mount
    return None

def save_selected_settings(selected_port, usb_mount):
    settings = {
        "USB_MOUNT": usb_mount,
        "EXPECTED_PORT": selected_port
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

if __name__ == "__main__":
    port = select_usb_port()
    if not port:
        print("No port selected.")
        exit(1)
    print(f"Selected port: {port}")

    mount = select_usb_mount()
    if not mount:
        print("No mount selected.")
        exit(1)
    print(f"Selected mount: {mount}")

    save_selected_settings(port, mount)
    print("USB port and mount selection saved.")