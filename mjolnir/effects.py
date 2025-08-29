"""
MJOLNIR Audio and Effects Module

This module provides audio feedback and visual effects to enhance
the dramatic user experience of MJOLNIR interactions.
"""

import time
import threading
import subprocess
import os

def play_system_sound(sound_type="default"):
    """Play system sounds for dramatic effect."""
    try:
        if sound_type == "warning":
            # System alert sound
            subprocess.run(["pactl", "play-sample", "bell"], 
                          capture_output=True, timeout=2)
        elif sound_type == "error":
            # Error sound (multiple beeps)
            for _ in range(3):
                subprocess.run(["pactl", "play-sample", "bell"], 
                              capture_output=True, timeout=1)
                time.sleep(0.2)
        elif sound_type == "success":
            # Success chime (higher pitch if available)
            subprocess.run(["pactl", "play-sample", "bell"], 
                          capture_output=True, timeout=2)
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        # Fallback to terminal bell if system sounds unavailable
        print("\a", end="", flush=True)

def dramatic_countdown_with_effects(seconds, message_prefix="", callback=None):
    """Enhanced countdown with sound and visual effects."""
    def countdown_with_sound():
        for i in range(seconds, 0, -1):
            if i <= 3:
                print(f"\033[91m🔥 {message_prefix} {i} seconds remaining! 🔥\033[0m")
                play_system_sound("warning")
                time.sleep(0.3)
                print(f"\033[91m{'!' * (4-i)}\033[0m")
            elif i <= 5:
                print(f"\033[93m⚡ {message_prefix} {i} seconds remaining... ⚡\033[0m")
                play_system_sound("warning")
            else:
                print(f"⏰ {message_prefix} {i} seconds remaining...")
            time.sleep(0.7 if i <= 3 else 1)
        
        print(f"\033[92m✨ {message_prefix} COMPLETE! ✨\033[0m")
        play_system_sound("success")
        if callback:
            callback()
    
    threading.Thread(target=countdown_with_sound, daemon=True).start()

def mjolnir_startup_sequence():
    """Dramatic startup sequence with effects."""
    startup_messages = [
        ("🌙 In the depths of Asgard...", 1.5),
        ("⚡ Ancient powers stir...", 1.0),
        ("🔨 MJOLNIR awakens from eternal slumber!", 1.5),
        ("⚡ The hammer recognizes its purpose...", 1.0),
        ("🛡️  Divine protection protocols: ONLINE", 1.0),
        ("✨ Ready to serve the worthy!", 0.5)
    ]
    
    for message, delay in startup_messages:
        print(f"\033[96m{message}\033[0m")
        if "awakens" in message or "ONLINE" in message:
            play_system_sound("success")
        time.sleep(delay)

def lockdown_alarm_sequence():
    """Dramatic lockdown alarm with escalating effects."""
    print("\033[91m" + "=" * 60 + "\033[0m")
    print("\033[91m🚨 UNAUTHORIZED ACCESS DETECTED! 🚨\033[0m")
    print("\033[91m" + "=" * 60 + "\033[0m")
    
    for i in range(5):
        print(f"\033[91m⚠️  SECURITY BREACH ALERT #{i+1} ⚠️\033[0m")
        play_system_sound("error")
        time.sleep(0.5)
    
    print("\033[93m🔥 MJOLNIR'S PROTECTIVE WRATH ACTIVATING... 🔥\033[0m")

def worthy_authentication_sequence():
    """Celebration sequence for successful authentication."""
    celebration_messages = [
        "🎉 THE WORTHY HAVE BEEN RECOGNIZED! 🎉",
        "⚡ Thor's blessing flows through the realm!",
        "🛡️  Divine protection is now active!",
        "✨ Welcome, chosen one! ✨"
    ]
    
    for message in celebration_messages:
        print(f"\033[92m{message}\033[0m")
        play_system_sound("success")
        time.sleep(0.8)

if __name__ == "__main__":
    print("🔨 MJOLNIR Audio Effects Test 🔨")
    mjolnir_startup_sequence()
    time.sleep(2)
    
    print("\nTesting countdown with effects...")
    dramatic_countdown_with_effects(5, "TEST SEQUENCE")
    time.sleep(6)
    
    print("\nTesting lockdown alarm...")
    lockdown_alarm_sequence()
    time.sleep(3)
    
    print("\nTesting authentication celebration...")
    worthy_authentication_sequence()