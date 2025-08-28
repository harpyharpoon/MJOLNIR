import tkinter as tk
from tkinter import messagebox, filedialog
import threading
from .usb_monitor import monitor_usb_events
from mjolnir.usb import select_usb_port, select_usb_mount, save_selected_settings
from mjolnir.hashing import generate_baseline, compare_with_baseline
from mjolnir.scheduler import periodic_hash_check
# from mjolnir.backup import backup_files
from mjolnir.config import get_mandatory_files, get_selected_files, set_selected_files
from mjolnir.hashing import generate_baseline

def select_usb_port_mount():
    selected_port = select_usb_port()
    if not selected_port:
        return
    selected_mount = select_usb_mount()
    if not selected_mount:
        return
    save_selected_settings(selected_port, selected_mount)
    # Optionally, show a message to the user
    messagebox.showinfo("USB Selection", f"Port: {selected_port}\nMount: {selected_mount} saved!")

def select_files_folders():
    recommended = get_mandatory_files(title="Recommended files/folders to be included")
    files = filedialog.askopenfilenames(title="Select Files/Folders for Hashing")
    folder = filedialog.askdirectory(title="Select Folder for Hashing")
    selected = list(files)
    if recommended:
        set_selected_files(recommended)
        messagebox.showinfo("Select Files/Folders", "Recommended files/folders selected.")
    if files:
        set_selected_files(files)
        messagebox.showinfo("Select Files/Folders", "File/folder selection completed.")
    if folder:
        set_selected_files(selected + [folder])
        messagebox.showinfo("Select Files/Folders", "File/folder selection completed.")
    if selected:
        set_selected_files(selected)
        messagebox.showinfo("Select Files/Folders", "File/folder selection completed.")
    else:
        messagebox.showwarning("Select Files/Folders", "No files or folders selected.")

def hash_format_config():
    # Call your hash format/config logic here
    messagebox.showinfo("Hash Format/Config", "Hash format/config dialog goes here.")

def generate_hash():
    selected_files = get_mandatory_files()
    if not selected_files:
        messagebox.showwarning("Generate Hash", "No files/folders selected for hashing.")
        return

    try:
        generate_baseline()
        messagebox.showinfo("Generate Hash", "Hash generation completed successfully.")
    except Exception as e:
        messagebox.showerror("Generate Hash", f"Error during hash generation:\n{e}")


def schedule_hash_pulls():
    # Call your scheduling logic here
    messagebox.showinfo("Schedule Hash Pulls", "Scheduling dialog goes here.")

def update_usb_status(is_trusted):
    def set_status():
        if is_trusted:
            status_label.config(text="Trusted USB Connected", bg="green", fg="white")
        else:
            status_label.config(text="No Trusted USB", bg="red", fg="white")
    root.after(0, set_status)

def start_usb_monitor():
    # Run the monitor in a separate thread so it doesn't block the GUI
    threading.Thread(target=monitor_usb_events, args=(update_usb_status,), daemon=True).start()

root = tk.Tk()
root.title("MJOLNIR Control Panel")

status_label = tk.Label(root, text="No Trusted USB", bg="red", fg="white", font=("Arial", 12, "bold"), width=30)
status_label.pack(pady=10)

tk.Label(root, text="MJOLNIR Main Menu", font=("Arial", 16, "bold")).pack(pady=10)

tk.Button(root, text="Select USB Port/Mount", width=30, command=select_usb_port_mount).pack(pady=5)
tk.Button(root, text="Select Files/Folders for Hash Generation", width=30, command=select_files_folders).pack(pady=5)
tk.Button(root, text="Hash Format and Config", width=30, command=hash_format_config).pack(pady=5)
tk.Button(root, text="Generate Hash for Selected Data", width=30, command=generate_hash).pack(pady=5)
tk.Button(root, text="Schedule Periodic Hash Pulls", width=30, command=schedule_hash_pulls).pack(pady=5)

tk.Button(root, text="Exit", width=30, command=root.quit).pack(pady=20)

start_usb_monitor()

root.mainloop()