# Flock You: Surveillance Device Scanner

<div align="center">
  <img src="flock.png" alt="Flock You Logo" width="300px">
  <h3>Turn the tables on surveillance.</h3>
</div>

**Flock You** (aka **Flock Drive**) is an advanced scanner that detects **Flock Safety** cameras, **Raven** gunshot detectors, and other surveillance devices using WiFi and Bluetooth signatures.

## Quick Start: Choose Your Weapon

| **Platform** | **Best For** | **Difficulty** | **Guide** |
| :--- | :--- | :--- | :--- |
| **Raspberry Pi** | **Dedicated Device**. Always-on scanning in your car (Headless). | Medium | [**Setup Guide (Pi)**](HELP_SETUP_PI.md) |
| **Laptop / Surface** | **On-the-Go Scanning**. PostmarketOS / Linux Laptops. | Easy | [**Setup Guide (PC)**](HELP_SETUP_PC.md) |
| **ESP32 (Hardware)** | **Pocket Carry**. Ultra-portable standalone device (Oui-Spy). | Hard (Soldering) | [**Setup Guide (ESP32)**](HELP_SETUP_ESP32.md) |

---

## Features

- **Multi-Method Detection**:
  - **WiFi**: Sniffs Probe Requests & Beacons (Monitor Mode).
  - **BLE**: Scans for specific Service UUIDs (Raven/ShotSpotter) and device names.
- **Audio Feedback**:
    - **System Audio**: Pygame-based alerts (HDMI/Jack).
    - **Browser Audio**: Beeps directly from the dashboard (great for laptops).
- **Tactical Dashboard**:
    - **Radar Mode**: Abstract proximity visualization.
    - **Map Mode**: Offline-ready street map with GPS tracking (Leaflet).
    - **Visual Alerts**: Full-screen "Red Flash" on critical detections.
- **GPS Logging**: Maps detections to KML/CSV files.

## Installation (Software)

For Raspberry Pi or Linux PC users, we have a unified **Easy Installer**:

1. **Clone the repo**:
   ```bash
   git clone https://github.com/colonelpanic/flock-you.git
   cd flock-you
   ```

2. **Run the installer**:
   ```bash
   sudo ./install.sh
   ```

3. **Follow the Wizard**:
   - Select **Dedicated Device** for Raspberry Pi (Service Mode).
   - Select **Personal Computer** for Laptop (Manual Mode).

## Laptop / Surface RT Usage

For devices like the Microsoft Surface RT running PostmarketOS, we provide a dedicated launch script that requires no system services.

1. **Connect Peripherals**: Plug in your USB GPS and ensure your WiFi card supports Monitor Mode.
2. **Launch**:
   ```bash
   sudo ./start_laptop.sh
   ```
3. **Open Dashboard**: Go to `http://localhost:5000` in your browser.
   - **Click the page** once to enable Audio Alerts.
   - Toggle **MAP** view to see your location (GPS fix required).
   - The screen will **FLASH RED** when a high-threat device is detected.

## Documentation

- [**Pi Setup Guide**](HELP_SETUP_PI.md) - Headless config, systemd service.
- [**PC Setup Guide**](HELP_SETUP_PC.md) - Monitor mode, manual running.
- [**ESP32 Setup Guide**](HELP_SETUP_ESP32.md) - Firmware flashing, wiring.
- [**API / Dashboard**](api/README.md) - Companion dashboard details.

## Legal Disclaimer

**For Educational and Research Purposes Only.**
This tool is designed to help researchers and privacy advocates understand the prevalence of surveillance technology.
- **Do not** use this tool to interfere with lawful operations.
- **Respect** local laws regarding wireless scanning and monitor mode.
- **Authors are not responsible** for misuse.

**Oui-Spy devices available at [colonelpanic.tech](https://colonelpanic.tech)**
