import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import threading
from .usb_monitor import monitor_usb_events
from mjolnir.usb import select_usb_port, select_usb_mount, save_selected_settings
from mjolnir.hashing import generate_baseline, compare_with_baseline, save_consolidated_hash, verify_consolidated_hash, get_hash_summary
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
    # Get current mandatory files for display
    mandatory_files = get_mandatory_files()
    
    # Show current recommended files/folders in a message
    current_files = []
    for category, files in mandatory_files.items():
        if category != "CUSTOM" and files:
            current_files.extend(files)
    
    if current_files:
        messagebox.showinfo(
            "Recommended files/folders", 
            f"Currently recommended files/folders:\n" + "\n".join(current_files[:10]) + 
            (f"\n... and {len(current_files) - 10} more" if len(current_files) > 10 else "")
        )
    
    # Allow user to select additional files
    files = filedialog.askopenfilenames(title="Select Additional Files for Hashing")
    folder = filedialog.askdirectory(title="Select Additional Folder for Hashing")
    
    # Build combined selection
    selected = list(files)
    if folder:
        selected.append(folder)
    
    if selected:
        # Get current custom files and add new selections
        current_custom = get_selected_files()
        # Combine and remove duplicates
        all_selected = list(set(current_custom + selected))
        set_selected_files(all_selected)
        messagebox.showinfo("Select Files/Folders", f"Added {len(selected)} new files/folders to selection.")
    else:
        messagebox.showinfo("Select Files/Folders", "No additional files or folders selected.")

def hash_format_config():
    """Open hash format and configuration dialog."""
    config_window = tk.Toplevel(root)
    config_window.title("Hash Format & Configuration")
    config_window.geometry("400x300")
    config_window.resizable(False, False)
    
    # Make window modal
    config_window.transient(root)
    config_window.grab_set()
    
    # Hash algorithm selection
    tk.Label(config_window, text="Hash Algorithm:", font=("Arial", 12, "bold")).pack(pady=10)
    
    hash_var = tk.StringVar(value="SHA256")
    hash_frame = tk.Frame(config_window)
    hash_frame.pack(pady=5)
    
    tk.Radiobutton(hash_frame, text="SHA256 (Recommended)", variable=hash_var, 
                   value="SHA256", state="normal").pack(anchor="w")
    tk.Radiobutton(hash_frame, text="SHA1 (Legacy)", variable=hash_var, 
                   value="SHA1", state="disabled").pack(anchor="w")
    tk.Radiobutton(hash_frame, text="MD5 (Not recommended)", variable=hash_var, 
                   value="MD5", state="disabled").pack(anchor="w")
    
    tk.Label(config_window, text="Note: Currently only SHA256 is supported", 
             fg="gray").pack(pady=5)
    
    # Hash rotation settings
    tk.Label(config_window, text="Hash Rotation Settings:", font=("Arial", 12, "bold")).pack(pady=(20, 10))
    
    rotation_frame = tk.Frame(config_window)
    rotation_frame.pack(pady=5)
    
    tk.Label(rotation_frame, text="Days between automatic hash checks:").pack(side="left")
    rotation_var = tk.StringVar(value="7")
    rotation_entry = tk.Entry(rotation_frame, textvariable=rotation_var, width=5)
    rotation_entry.pack(side="left", padx=(5, 0))
    
    # Baseline location
    tk.Label(config_window, text="Configuration:", font=("Arial", 12, "bold")).pack(pady=(20, 10))
    
    info_text = tk.Text(config_window, height=4, width=45, wrap=tk.WORD)
    info_text.pack(pady=5)
    
    try:
        from mjolnir.config import get_settings
        settings = get_settings()
        usb_mount = settings.get("USB_MOUNT", "Not configured")
        expected_port = settings.get("EXPECTED_PORT", "Not configured")
        rotation_days = settings.get("HASH_ROTATION_DAYS", 7)
        rotation_var.set(str(rotation_days))
        
        info_text.insert("1.0", f"USB Mount: {usb_mount}\n")
        info_text.insert("end", f"Expected Port: {expected_port}\n")
        info_text.insert("end", f"Hash files stored on USB device\n")
        info_text.insert("end", f"Current algorithm: SHA256")
    except Exception as e:
        info_text.insert("1.0", f"Error reading configuration: {e}")
    
    info_text.config(state="disabled")
    
    # Buttons
    button_frame = tk.Frame(config_window)
    button_frame.pack(pady=20)
    
    def save_config():
        try:
            from mjolnir.config import get_settings, update_settings
            settings = get_settings()
            new_rotation = int(rotation_var.get())
            if new_rotation < 1:
                messagebox.showerror("Invalid Input", "Rotation days must be at least 1")
                return
            settings["HASH_ROTATION_DAYS"] = new_rotation
            update_settings(settings)
            messagebox.showinfo("Success", "Configuration saved successfully!")
            config_window.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for rotation days")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    tk.Button(button_frame, text="Save", command=save_config).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=config_window.destroy).pack(side="left", padx=5)

def generate_hash():
    selected_files = get_mandatory_files()
    if not selected_files:
        messagebox.showwarning("Generate Hash", "No files/folders selected for hashing.")
        return

    try:
        generate_baseline()
        # Also generate consolidated hash
        consolidated_file = save_consolidated_hash()
        if consolidated_file:
            messagebox.showinfo("Generate Hash", 
                              "Hash generation completed successfully.\n" +
                              f"Baseline and consolidated hashes saved.\n" +
                              f"Consolidated hash file: {os.path.basename(consolidated_file)}")
        else:
            messagebox.showinfo("Generate Hash", "Baseline hash generation completed successfully.")
    except Exception as e:
        messagebox.showerror("Generate Hash", f"Error during hash generation:\n{e}")

def verify_hash_integrity():
    """Verify hash integrity using consolidated hash."""
    try:
        # First show current hash summary
        summary = get_hash_summary()
        
        if not summary["baseline_exists"]:
            messagebox.showwarning("Verify Integrity", "No baseline hash found. Generate hashes first.")
            return
        
        summary_text = f"Hash Summary:\n"
        summary_text += f"Total files: {summary['file_count']}\n"
        summary_text += f"Categories: {len(summary['categories'])}\n"
        for category, count in summary['categories'].items():
            summary_text += f"  - {category}: {count} files\n"
        
        if summary['consolidated_hash']:
            summary_text += f"\nConsolidated hash: {summary['consolidated_hash'][:16]}...\n"
        
        summary_text += "\nVerifying integrity..."
        
        # Show summary first
        messagebox.showinfo("Hash Summary", summary_text)
        
        # Perform verification
        success = verify_consolidated_hash()
        
        if success:
            messagebox.showinfo("Verification Success", 
                              "✓ Hash verification PASSED\n" +
                              "All files match the stored baseline.")
        else:
            messagebox.showerror("Verification Failed", 
                               "✗ Hash verification FAILED\n" +
                               "Some files have been modified or are missing.\n" +
                               "Check the console output for details.")
            
    except Exception as e:
        messagebox.showerror("Verification Error", f"Error during verification:\n{e}")

def show_hash_status():
    """Show detailed hash status window."""
    status_window = tk.Toplevel(root)
    status_window.title("Hash Status & Summary")
    status_window.geometry("600x400")
    status_window.resizable(True, True)
    
    # Make window modal
    status_window.transient(root)
    status_window.grab_set()
    
    # Title
    tk.Label(status_window, text="Hash Status & Summary", font=("Arial", 14, "bold")).pack(pady=10)
    
    # Create scrollable text widget
    text_frame = tk.Frame(status_window)
    text_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
    scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Get hash summary
    try:
        summary = get_hash_summary()
        
        status_text = "=== MJOLNIR Hash Status ===\n\n"
        
        if summary["baseline_exists"]:
            status_text += f"✓ Baseline hash file exists\n"
            status_text += f"📁 Total files monitored: {summary['file_count']}\n"
            status_text += f"📂 Categories: {len(summary['categories'])}\n\n"
            
            status_text += "Category breakdown:\n"
            for category, count in summary['categories'].items():
                status_text += f"  • {category}: {count} files\n"
            
            if summary['consolidated_hash']:
                status_text += f"\n🔐 Consolidated master hash:\n"
                status_text += f"   {summary['consolidated_hash']}\n"
            
            if summary['last_updated']:
                import datetime
                last_update = datetime.datetime.fromtimestamp(summary['last_updated'])
                status_text += f"\n🕒 Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            status_text += "⚠️  No baseline hash file found\n"
            status_text += "    Run 'Generate Hash for Selected Data' first\n"
        
        # Check for consolidated hash file
        try:
            from mjolnir.config import get_usb_mount
            usb_mount = get_usb_mount()
            if usb_mount:
                consolidated_file = os.path.join(usb_mount, "consolidated_hashes.json")
                if os.path.exists(consolidated_file):
                    status_text += f"\n✓ Consolidated hash file exists on USB\n"
                    status_text += f"   Location: {consolidated_file}\n"
                else:
                    status_text += f"\n⚠️  No consolidated hash file on USB\n"
                    status_text += f"   Generate hashes to create it\n"
            else:
                status_text += f"\n⚠️  USB mount not configured\n"
        except Exception as e:
            status_text += f"\n❌ Error checking USB status: {e}\n"
            
        text_widget.insert("1.0", status_text)
        text_widget.config(state="disabled")
        
    except Exception as e:
        error_text = f"❌ Error loading hash status:\n{e}"
        text_widget.insert("1.0", error_text)
        text_widget.config(state="disabled")
    
    # Buttons
    button_frame = tk.Frame(status_window)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Refresh", 
              command=lambda: status_window.destroy() or show_hash_status()).pack(side="left", padx=5)
    tk.Button(button_frame, text="Verify Integrity", 
              command=lambda: status_window.destroy() or verify_hash_integrity()).pack(side="left", padx=5)
    tk.Button(button_frame, text="Close", command=status_window.destroy).pack(side="left", padx=5)


def schedule_hash_pulls():
    """Open periodic hash pull scheduler dialog."""
    scheduler_window = tk.Toplevel(root)
    scheduler_window.title("Schedule Periodic Hash Pulls")
    scheduler_window.geometry("450x350")
    scheduler_window.resizable(False, False)
    
    # Make window modal
    scheduler_window.transient(root)
    scheduler_window.grab_set()
    
    # Current status
    tk.Label(scheduler_window, text="Hash Pull Scheduler", font=("Arial", 14, "bold")).pack(pady=10)
    
    status_frame = tk.Frame(scheduler_window)
    status_frame.pack(pady=10, fill="x", padx=20)
    
    # Check current status
    try:
        from mjolnir.scheduler import get_last_hash_check
        from mjolnir.config import get_hash_rotation_days
        from datetime import datetime
        
        last_check = get_last_hash_check()
        rotation_days = get_hash_rotation_days()
        
        status_text = tk.Text(status_frame, height=6, wrap=tk.WORD)
        status_text.pack(fill="both", expand=True)
        
        if last_check:
            days_since = (datetime.now() - last_check).days
            next_check_in = max(0, rotation_days - days_since)
            status_text.insert("1.0", f"Last hash check: {last_check.strftime('%Y-%m-%d %H:%M:%S')}\n")
            status_text.insert("end", f"Days since last check: {days_since}\n")
            status_text.insert("end", f"Rotation interval: {rotation_days} days\n")
            status_text.insert("end", f"Next check due in: {next_check_in} days\n")
            status_text.insert("end", f"Status: {'Overdue' if next_check_in == 0 else 'Scheduled'}\n")
        else:
            status_text.insert("1.0", "No previous hash check found.\n")
            status_text.insert("end", f"Rotation interval: {rotation_days} days\n")
            status_text.insert("end", "Status: Never run\n")
            
        status_text.config(state="disabled")
        
    except Exception as e:
        status_text = tk.Label(status_frame, text=f"Error reading status: {e}", fg="red")
        status_text.pack()
    
    # Manual controls
    tk.Label(scheduler_window, text="Manual Actions", font=("Arial", 12, "bold")).pack(pady=(20, 10))
    
    button_frame = tk.Frame(scheduler_window)
    button_frame.pack(pady=10)
    
    def run_immediate_check():
        try:
            from mjolnir.scheduler import periodic_hash_check
            
            # Run in a separate thread to avoid blocking GUI
            def run_check():
                try:
                    periodic_hash_check()
                    root.after(0, lambda: messagebox.showinfo("Success", "Hash check completed successfully!"))
                except Exception as e:
                    root.after(0, lambda: messagebox.showerror("Error", f"Hash check failed: {e}"))
                    
            threading.Thread(target=run_check, daemon=True).start()
            scheduler_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start hash check: {e}")
    
    def force_reset_schedule():
        try:
            from mjolnir.scheduler import set_last_hash_check
            from datetime import datetime
            
            result = messagebox.askyesno(
                "Reset Schedule", 
                "This will reset the schedule as if a hash check was just completed. Continue?"
            )
            if result:
                set_last_hash_check(datetime.now())
                messagebox.showinfo("Success", "Schedule reset successfully!")
                scheduler_window.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset schedule: {e}")
    
    def configure_interval():
        try:
            from mjolnir.config import get_settings, update_settings
            current_days = get_settings().get("HASH_ROTATION_DAYS", 7)
            
            new_days = simpledialog.askinteger(
                "Configure Interval",
                f"Enter new rotation interval in days (current: {current_days}):",
                initialvalue=current_days,
                minvalue=1,
                maxvalue=365
            )
            
            if new_days:
                settings = get_settings()
                settings["HASH_ROTATION_DAYS"] = new_days
                update_settings(settings)
                messagebox.showinfo("Success", f"Rotation interval set to {new_days} days!")
                scheduler_window.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update interval: {e}")
    
    tk.Button(button_frame, text="Run Hash Check Now", command=run_immediate_check, 
              bg="lightgreen").pack(side="left", padx=5)
    tk.Button(button_frame, text="Reset Schedule", command=force_reset_schedule, 
              bg="orange").pack(side="left", padx=5)
    
    tk.Button(scheduler_window, text="Configure Interval", command=configure_interval, 
              bg="lightblue").pack(pady=10)
    
    # Info
    info_label = tk.Label(scheduler_window, 
                         text="The scheduler automatically runs hash checks based on the configured interval.\n" +
                              "Manual actions above allow immediate control over the schedule.",
                         wraplength=400, justify="center", fg="gray")
    info_label.pack(pady=10)
    
    # Close button
    tk.Button(scheduler_window, text="Close", command=scheduler_window.destroy).pack(pady=10)

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
tk.Button(root, text="Verify Hash Integrity", width=30, command=verify_hash_integrity).pack(pady=5)
tk.Button(root, text="Show Hash Status & Summary", width=30, command=show_hash_status).pack(pady=5)
tk.Button(root, text="Schedule Periodic Hash Pulls", width=30, command=schedule_hash_pulls).pack(pady=5)

tk.Button(root, text="Exit", width=30, command=root.quit).pack(pady=20)

start_usb_monitor()

root.mainloop()