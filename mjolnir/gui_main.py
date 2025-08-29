import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import threading
import time
from .usb_monitor import monitor_usb_events
from mjolnir.usb import select_usb_port, select_usb_mount, save_selected_settings
from mjolnir.hashing import generate_baseline, compare_with_baseline
from mjolnir.scheduler import periodic_hash_check
# from mjolnir.backup import backup_files
from mjolnir.config import get_mandatory_files, get_selected_files, set_selected_files
from mjolnir.hashing import generate_baseline

# MJOLNIR Color Scheme
MJOLNIR_COLORS = {
    'bg_primary': '#1a1a2e',      # Dark blue-black
    'bg_secondary': '#16213e',     # Darker blue
    'accent_gold': '#eee657',      # Thor's golden accent
    'accent_blue': '#0f3460',      # Deep blue
    'text_light': '#ffffff',       # White text
    'text_gold': '#eee657',        # Golden text
    'trusted_green': '#00ff88',    # Bright green for trusted
    'danger_red': '#ff0040',       # Bright red for danger
    'warning_orange': '#ff8c00'    # Orange for warnings
}

def mjolnir_style_window(window):
    """Apply MJOLNIR theme to a window."""
    window.configure(bg=MJOLNIR_COLORS['bg_primary'])

def create_mjolnir_button(parent, text, command, width=30, color_scheme='normal'):
    """Create a MJOLNIR-themed button."""
    if color_scheme == 'danger':
        bg_color = MJOLNIR_COLORS['danger_red']
        fg_color = MJOLNIR_COLORS['text_light']
    elif color_scheme == 'success':
        bg_color = MJOLNIR_COLORS['trusted_green']
        fg_color = MJOLNIR_COLORS['bg_primary']
    elif color_scheme == 'warning':
        bg_color = MJOLNIR_COLORS['warning_orange']
        fg_color = MJOLNIR_COLORS['bg_primary']
    else:
        bg_color = MJOLNIR_COLORS['accent_blue']
        fg_color = MJOLNIR_COLORS['text_light']
    
    return tk.Button(parent, text=text, width=width, command=command,
                     bg=bg_color, fg=fg_color, font=("Arial", 10, "bold"),
                     relief="raised", bd=2, activebackground=MJOLNIR_COLORS['accent_gold'])

def create_mjolnir_label(parent, text, font_size=12, text_color='light'):
    """Create a MJOLNIR-themed label."""
    color = MJOLNIR_COLORS['text_light'] if text_color == 'light' else MJOLNIR_COLORS['text_gold']
    return tk.Label(parent, text=text, bg=MJOLNIR_COLORS['bg_primary'], 
                    fg=color, font=("Arial", font_size, "bold"))

def dramatic_status_update(message, delay=0.05):
    """Update status with dramatic character reveal."""
    def animate():
        current_text = ""
        for i, char in enumerate(message):
            current_text += char
            status_detail_label.config(text=current_text)
            root.update()
            time.sleep(delay)
    
    threading.Thread(target=animate, daemon=True).start()

def select_usb_port_mount():
    dramatic_status_update("🔨 Seeking the sacred connection points...")
    time.sleep(1)
    
    selected_port = select_usb_port()
    if not selected_port:
        dramatic_status_update("❌ The realms remain unbound")
        return
        
    dramatic_status_update("⚡ Port chosen... Now seeking the sacred mount...")
    time.sleep(0.5)
    
    selected_mount = select_usb_mount()
    if not selected_mount:
        dramatic_status_update("❌ The mount eludes us")
        return
        
    save_selected_settings(selected_port, selected_mount)
    dramatic_status_update("✨ Sacred bindings complete! MJOLNIR is ready!")
    # Optionally, show a message to the user
    messagebox.showinfo("⚡ MJOLNIR Configuration ⚡", 
                       f"🔨 Sacred Port: {selected_port}\n⛰️  Divine Mount: {selected_mount}\n\n✅ Configuration blessed by Thor!")

def select_files_folders():
    dramatic_status_update("🔍 Scanning the Nine Realms for precious artifacts...")
    time.sleep(1)
    
    # Get current mandatory files for display
    mandatory_files = get_mandatory_files()
    
    # Show current recommended files/folders in a message
    current_files = []
    for category, files in mandatory_files.items():
        if category != "CUSTOM" and files:
            current_files.extend(files)
    
    if current_files:
        messagebox.showinfo(
            "🛡️  Sacred Artifacts Registry", 
            f"⚡ Currently protected treasures:\n\n" + "\n".join(current_files[:10]) + 
            (f"\n\n... and {len(current_files) - 10} more divine artifacts" if len(current_files) > 10 else "")
        )
    
    dramatic_status_update("📂 Choose additional artifacts to guard...")
    # Allow user to select additional files
    files = filedialog.askopenfilenames(title="🔨 Select Files Worthy of MJOLNIR's Protection")
    dramatic_status_update("📁 Choose folders to shield from harm...")
    folder = filedialog.askdirectory(title="⚡ Select Folder for Divine Protection")
    
    # Build combined selection
    selected = list(files)
    if folder:
        selected.append(folder)
    
    if selected:
        dramatic_status_update("✨ Consecrating new artifacts...")
        time.sleep(1)
        # Get current custom files and add new selections
        current_custom = get_selected_files()
        # Combine and remove duplicates
        all_selected = list(set(current_custom + selected))
        set_selected_files(all_selected)
        dramatic_status_update(f"🎉 {len(selected)} new artifacts added to MJOLNIR's protection!")
        messagebox.showinfo("⚡ Divine Protection Extended ⚡", 
                           f"🛡️  Added {len(selected)} new treasures to the vault!\n\n✨ MJOLNIR's watch grows stronger!")
    else:
        dramatic_status_update("😔 No new artifacts chosen for protection")
        messagebox.showinfo("🔨 MJOLNIR Status 🔨", "⚡ No additional artifacts selected for divine protection")

def hash_format_config():
    """Open hash format and configuration dialog."""
    dramatic_status_update("⚙️  Opening the sacred configuration chamber...")
    
    config_window = tk.Toplevel(root)
    config_window.title("🔨 MJOLNIR Cryptographic Configuration")
    config_window.geometry("450x350")
    config_window.resizable(False, False)
    mjolnir_style_window(config_window)
    
    # Make window modal
    config_window.transient(root)
    config_window.grab_set()
    
    # Hash algorithm selection
    create_mjolnir_label(config_window, "⚡ Divine Hash Algorithm ⚡", 14).pack(pady=15)
    
    hash_var = tk.StringVar(value="SHA256")
    hash_frame = tk.Frame(config_window, bg=MJOLNIR_COLORS['bg_primary'])
    hash_frame.pack(pady=10)
    
    tk.Radiobutton(hash_frame, text="🔨 SHA256 (Thor's Blessing)", variable=hash_var, 
                   value="SHA256", state="normal", bg=MJOLNIR_COLORS['bg_primary'],
                   fg=MJOLNIR_COLORS['text_light'], selectcolor=MJOLNIR_COLORS['accent_blue']).pack(anchor="w")
    tk.Radiobutton(hash_frame, text="⚡ SHA1 (Ancient Runes)", variable=hash_var, 
                   value="SHA1", state="disabled", bg=MJOLNIR_COLORS['bg_primary'],
                   fg=MJOLNIR_COLORS['text_light'], selectcolor=MJOLNIR_COLORS['accent_blue']).pack(anchor="w")
    tk.Radiobutton(hash_frame, text="💀 MD5 (Forbidden Magic)", variable=hash_var, 
                   value="MD5", state="disabled", bg=MJOLNIR_COLORS['bg_primary'],
                   fg=MJOLNIR_COLORS['text_light'], selectcolor=MJOLNIR_COLORS['accent_blue']).pack(anchor="w")
    
    tk.Label(config_window, text="⚠️  Only SHA256 bears Thor's divine blessing", 
             fg=MJOLNIR_COLORS['warning_orange'], bg=MJOLNIR_COLORS['bg_primary']).pack(pady=5)
    
    # Hash rotation settings
    create_mjolnir_label(config_window, "🔄 Sacred Rotation Rituals", 14).pack(pady=(25, 15))
    
    rotation_frame = tk.Frame(config_window, bg=MJOLNIR_COLORS['bg_primary'])
    rotation_frame.pack(pady=10)
    
    tk.Label(rotation_frame, text="Days between divine inspections:", 
             bg=MJOLNIR_COLORS['bg_primary'], fg=MJOLNIR_COLORS['text_light']).pack(side="left")
    rotation_var = tk.StringVar(value="7")
    rotation_entry = tk.Entry(rotation_frame, textvariable=rotation_var, width=5,
                             bg=MJOLNIR_COLORS['bg_secondary'], fg=MJOLNIR_COLORS['text_gold'])
    rotation_entry.pack(side="left", padx=(5, 0))
    
    # Baseline location
    create_mjolnir_label(config_window, "⚙️  Divine Configuration", 14).pack(pady=(25, 15))
    
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
    dramatic_status_update("🔨 Awakening MJOLNIR's cryptographic powers...")
    time.sleep(1)
    
    selected_files = get_mandatory_files()
    if not selected_files:
        dramatic_status_update("❌ No artifacts chosen for divine protection")
        messagebox.showwarning("⚡ MJOLNIR Warning ⚡", 
                              "🛡️  No files/folders selected for divine hashing.\n\n🔨 Please choose artifacts to protect first!")
        return

    dramatic_status_update("⚡ Forging cryptographic seals of protection...")
    countdown_timer_display(3, "Seal Creation")
    
    try:
        # Show progress with dramatic updates
        dramatic_status_update("🔥 The hammer's power flows through sacred algorithms...")
        time.sleep(2)
        
        generate_baseline()
        
        dramatic_status_update("✨ Divine protection seals have been forged! ✨")
        messagebox.showinfo("🔨 MJOLNIR Success 🔨", 
                           "⚡ Hash generation completed with Thor's blessing!\n\n🛡️  Your artifacts are now protected by divine cryptography!")
    except Exception as e:
        dramatic_status_update("💥 The forging process encountered resistance!")
        messagebox.showerror("🔥 MJOLNIR Error 🔥", 
                            f"⚠️  Error during divine hash forging:\n\n💀 {e}\n\n⚡ The realms require attention!")

def schedule_hash_pulls():
    """Open periodic hash pull scheduler dialog."""
    dramatic_status_update("📅 Opening the sacred calendar chamber...")
    
    scheduler_window = tk.Toplevel(root)
    scheduler_window.title("🔮 MJOLNIR Temporal Scheduling 🔮")
    scheduler_window.geometry("500x400")
    scheduler_window.resizable(False, False)
    mjolnir_style_window(scheduler_window)
    
    # Make window modal
    scheduler_window.transient(root)
    scheduler_window.grab_set()
    
    # Current status
    create_mjolnir_label(scheduler_window, "⏰ Sacred Ritual Scheduler ⏰", 16, 'gold').pack(pady=15)
    
    status_frame = tk.Frame(scheduler_window, bg=MJOLNIR_COLORS['bg_primary'])
    status_frame.pack(pady=15, fill="x", padx=25)
    
    # Check current status
    try:
        from mjolnir.scheduler import get_last_hash_check
        from mjolnir.config import get_hash_rotation_days
        from datetime import datetime
        
        last_check = get_last_hash_check()
        rotation_days = get_hash_rotation_days()
        
        status_text = tk.Text(status_frame, height=6, wrap=tk.WORD,
                             bg=MJOLNIR_COLORS['bg_secondary'], fg=MJOLNIR_COLORS['text_light'],
                             font=("Arial", 10))
        status_text.pack(fill="both", expand=True)
        
        if last_check:
            days_since = (datetime.now() - last_check).days
            next_check_in = max(0, rotation_days - days_since)
            status_text.insert("1.0", f"⚡ Last divine inspection: {last_check.strftime('%Y-%m-%d %H:%M:%S')}\n")
            status_text.insert("end", f"🕐 Days since last ritual: {days_since}\n")
            status_text.insert("end", f"⚙️  Sacred interval: {rotation_days} days\n")
            status_text.insert("end", f"⏳ Next ritual due in: {next_check_in} days\n")
            status_text.insert("end", f"🔮 Status: {'🔥 OVERDUE - MJOLNIR DEMANDS ACTION!' if next_check_in == 0 else '✅ Scheduled and blessed'}\n")
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
            status_label.config(text="⚡ THE WORTHY HAVE RETURNED ⚡", 
                              bg=MJOLNIR_COLORS['trusted_green'], fg=MJOLNIR_COLORS['bg_primary'])
            dramatic_status_update("🛡️  Divine protection flows through the realm...")
        else:
            status_label.config(text="💀 MJOLNIR AWAITS THE WORTHY 💀", 
                              bg=MJOLNIR_COLORS['danger_red'], fg=MJOLNIR_COLORS['text_light'])
            dramatic_status_update("⏳ The chosen one has not yet awakened...")
    root.after(0, set_status)

def countdown_timer_display(seconds, purpose="Operation"):
    """Display a dramatic countdown in the status area."""
    def countdown():
        for i in range(seconds, 0, -1):
            if i <= 3:
                dramatic_status_update(f"🔥 {purpose}: {i} 🔥", delay=0.02)
            elif i <= 5:
                dramatic_status_update(f"⚡ {purpose}: {i} ⚡", delay=0.03)
            else:
                dramatic_status_update(f"⏰ {purpose}: {i}")
            time.sleep(1)
        dramatic_status_update(f"✨ {purpose} COMPLETE! ✨")
    
    threading.Thread(target=countdown, daemon=True).start()

def start_usb_monitor():
    # Run the monitor in a separate thread so it doesn't block the GUI
    dramatic_status_update("🔍 Initiating eternal vigil...")
    threading.Thread(target=monitor_usb_events, args=(update_usb_status,), daemon=True).start()

# Create main window with MJOLNIR styling
root = tk.Tk()
root.title("🔨 MJOLNIR Command Throne 🔨")
root.geometry("600x700")
mjolnir_style_window(root)

# Title with dramatic styling
title_frame = tk.Frame(root, bg=MJOLNIR_COLORS['bg_primary'])
title_frame.pack(pady=20)

create_mjolnir_label(title_frame, "⚡ MJOLNIR ⚡", 24, 'gold').pack()
create_mjolnir_label(title_frame, "Thor's Divine Security Hammer", 12, 'light').pack()

# Status display with enhanced styling
status_frame = tk.Frame(root, bg=MJOLNIR_COLORS['bg_primary'])
status_frame.pack(pady=15)

status_label = tk.Label(status_frame, text="💀 MJOLNIR AWAITS THE WORTHY 💀", 
                       bg=MJOLNIR_COLORS['danger_red'], fg=MJOLNIR_COLORS['text_light'], 
                       font=("Arial", 12, "bold"), width=35, relief="raised", bd=3)
status_label.pack(pady=5)

# Status detail for dramatic updates
status_detail_label = tk.Label(status_frame, text="🌙 The realm slumbers in anticipation...", 
                              bg=MJOLNIR_COLORS['bg_primary'], fg=MJOLNIR_COLORS['text_gold'],
                              font=("Arial", 10), width=50, wraplength=400)
status_detail_label.pack(pady=5)

# Main menu with enhanced styling
menu_frame = tk.Frame(root, bg=MJOLNIR_COLORS['bg_primary'])
menu_frame.pack(pady=20)

create_mjolnir_label(menu_frame, "🛡️  DIVINE COMMAND CENTER 🛡️", 16, 'gold').pack(pady=15)

# Enhanced buttons with MJOLNIR styling
create_mjolnir_button(menu_frame, "🔗 Consecrate Sacred Ports", select_usb_port_mount, 35).pack(pady=8)
create_mjolnir_button(menu_frame, "📦 Choose Artifacts to Guard", select_files_folders, 35).pack(pady=8)
create_mjolnir_button(menu_frame, "⚙️  Configure Divine Magic", hash_format_config, 35).pack(pady=8)
create_mjolnir_button(menu_frame, "🔨 Forge Protection Seals", generate_hash, 35, 'success').pack(pady=8)
create_mjolnir_button(menu_frame, "📅 Schedule Sacred Rituals", schedule_hash_pulls, 35, 'warning').pack(pady=8)

# Separation line
separator = tk.Frame(root, height=2, bg=MJOLNIR_COLORS['accent_gold'])
separator.pack(fill="x", padx=50, pady=20)

# Exit button with dramatic styling
create_mjolnir_button(root, "⚡ Return MJOLNIR to Slumber ⚡", root.quit, 30, 'danger').pack(pady=20)

# Initialize the eternal watch
start_usb_monitor()

root.mainloop()