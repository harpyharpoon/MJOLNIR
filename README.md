MJOLNIR

MJOLNIR is a USB-based security tool designed with a simple yet powerful “lockdown” feature. It’s aimed at developers or security-conscious users who want an automated way to protect important files and system configurations when they notice suspicious activity.

Overview

Designated USB Port Protection: Assign a dedicated USB port for normal usage. If the USB is connected to any other port, MJOLNIR triggers a lockdown sequence.

Automated File Collection: Pulls important directories and system files, ensuring critical data is backed up before a potential compromise.

Integrity Verification: Generates SHA256 hashes for mandatory files and directories to detect tampering or unexpected changes.

Root Security Actions: Can automatically change root passwords and enforce security lockdown procedures.

KeePass and Security Tool Integration: Automatically launches a secure password database and optionally opens other security tools like Wireshark or Cockpit for quick access.

Extensible Features: Future development may include GitHub repository pulls, custom scripts, or additional automated security measures.

Use Cases

Protect critical data in the event of unexpected or unauthorized USB access.

Quickly initiate a system lockdown when something seems off.

Provide inexperienced developers or system administrators a simple, automated tool for security response.

Development Status

IN DEVELOPMENT: Core functionality like USB monitoring, file backup, hash verification, and trusted USB detection is implemented. Planned features include enhanced lockdown scripts, GitHub integration, and a configurable dashboard for security tools.
