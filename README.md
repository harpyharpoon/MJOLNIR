# MJOLNIR

MJOLNIR is a USB-based security tool designed for developers and security-conscious users who want an automated, hardware-assisted way to protect critical systems. With advanced features like port-based lockdown, password rotation reminders, NFC authentication, and enterprise/team integration, MJOLNIR is your first line of defense against unauthorized access and security lapses.

---

## Features

### 1. Designated USB Port Protection
- Assign a specific USB port as "trusted."
- If MJOLNIR is plugged into any other port, the device triggers a lockdown sequence.

### 2. NFC-Backed Lockdown Redundancy
- **Redundant NFC authentication:** Before executing lockdown/shutdown on a trigger port event, MJOLNIR requires a tap from a registered NFC security key.
- If the NFC key is not presented within a configurable timeout, MJOLNIR can either proceed with lockdown, log the event, or escalate (configurable).

### 3. Automated File Collection & Backup
- Collects and backs up specified directories and system files before a potential compromise.

### 4. Integrity Verification
- Generates SHA256 hashes for monitored files and directories to detect tampering or unauthorized changes.

### 5. Root Security Actions
- Can automatically change root passwords and enforce additional lockdown procedures.

### 6. Password Rotation Timer & Reminders
- Lets users (or IT admins) specify which critical accounts, databases, or services require regular password rotation.
- Configurable reminder intervals (e.g., every 14 or 30 days).
- Supports integration with password managers (e.g., KeePassXC) and custom password reset scripts.
- Notifies users/admins when rotations are due, logs rotation events, and tracks compliance.

### 7. KeePass and Security Tool Integration
- Optionally launches a secure password database (KeePassXC) and/or other security tools (like Wireshark, Cockpit) for rapid response.

### 8. Team & Enterprise Integration ("USB Keyring" Mode)
- **Centralized management:** IT departments can configure teams of MJOLNIR USB keyrings.
- **Networked sync:** Devices upload usage logs, password rotation status, and trigger events to an in-house server/dashboard over the secure company network.
- **Audit & compliance:** Central dashboard monitors:
  - Which users plugged in where and how often.
  - Which passwords were changed and when.
  - Which users are overdue for password rotation.
  - Any unauthorized port events or failed NFC authentication attempts.
- **Policy distribution:** Admins can update security policies, password rotation rules, and authorized NFC keys centrally.

---

## Example Log Data

```json
{
  "user_id": "jdoe",
  "device_id": "mjolnir-xyz123",
  "events": [
    {"timestamp": "2025-08-24T15:03:00Z", "event": "usb_plug", "port": "USB3-left"},
    {"timestamp": "2025-08-24T15:03:05Z", "event": "password_rotated", "account": "root"},
    {"timestamp": "2025-08-21T08:44:12Z", "event": "usb_plug", "port": "USB2-right"}
  ],
  "rotation_status": [
    {"account": "root", "last_rotated": "2025-08-24", "next_due": "2025-09-24"},
    {"account": "KeePassXC", "last_rotated": "2025-08-15", "next_due": "2025-08-29"}
  ]
}
```

---

## Password Rotation Configuration Example

```yaml
passwords:
  - name: root
    method: script:/usr/local/bin/reset_root_pw.sh
    interval_days: 30
    last_rotated: 2025-08-01
  - name: KeePassXC
    method: open_keepassxc
    interval_days: 14
    last_rotated: 2025-08-10
```

---

## Upcoming & Planned Features

- **Network Kill Switch:** Instantly disables all network adapters to isolate the system in an emergency.
- **Router and Network Log Retrieval:** Automatically pulls logs from designated routers or network devices for forensic analysis.
- **Strict Internet Access Control:** MJOLNIR will not connect to the internet unless both the designated USB and NFC authentication are present and validated.
- **Expanded NFC Authentication:** For additional actions beyond shutdown/lockdown.
- **Custom Scripts:** Allow IT teams to deploy custom response actions centrally.

---

## Deployment and Usage

1. **Configure** your designated USB port and authorized NFC keys.
2. **Set up** password rotation rules and tracked accounts via YAML config.
3. **(Optional for Enterprise)** Connect MJOLNIR clients to your in-house central management server to enable team monitoring and compliance reporting.
4. **Plug in:** MJOLNIR will monitor port usage, track and remind about password rotations, and require NFC authentication before any automated lockdown.

---

## Contributing

- Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Disclaimer

MJOLNIR is IN DEVELOPMENT. Use at your own risk. Test thoroughly in a controlled environment before deploying to production systems.
