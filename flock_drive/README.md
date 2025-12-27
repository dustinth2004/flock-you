# Flock Drive

A lightweight, portable surveillance device scanner designed for Raspberry Pi (Zero/3/4/5) and Laptops. Detects **Flock Safety** cameras and **Raven** gunshot detectors using WiFi and BLE signatures.

## Features
- **Cyberpunk Dashboard**: Real-time web interface (Dark Mode) for phones/screens.
- **GPS Logging**: Logs detections with coordinates to CSV and KML.
- **Audio Feedback**: High-quality tactical alerts via System Audio (3.5mm/HDMI) or GPIO Buzzer.
- **BLE Scanning**: Detects devices by Name, MAC Prefix, and Service UUIDs (Raven).
- **WiFi Scanning**: Sniffs Probe Requests and Beacons for target SSIDs/MACs (Monitor Mode required).
- **Headless Mode**: Runs as a systemd service on Raspberry Pi.

## Hardware Requirements
- **Raspberry Pi** (Zero W, 3B+, 4, 5) or Laptop (Linux).
- **GPS Dongle** (USB).
- **WiFi Adapter** (Optional, for WiFi scanning. Must support Monitor Mode).
- **Audio**:
    - **Option A**: 3.5mm Jack -> Speaker (requires Amplifier or Active Speaker).
    - **Option B**: Piezo Buzzer (GPIO 18).

## Installation

1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd flock-you
   ```

2. Run the installer (requires root):
   ```bash
   sudo ./install.sh
   ```

3. Start the service:
   ```bash
   sudo systemctl start flockdrive
   ```

## Usage

### Web Dashboard
Open `http://<IP_ADDRESS>:5000` in your browser.
- **Radar**: Visualizes proximity based on RSSI.
- **Threat Meter**: Shows highest current threat level.
- **Feed**: Live log of intercepted signals.

### Manual Run
```bash
# Activate venv
source /opt/flock_drive/venv/bin/activate

# Run
python -m flock_drive.main --gps-port /dev/ttyUSB0 --wifi-interface wlan1
```

### Command Line Arguments
- `--web-port`: Port for dashboard (default 5000)
- `--buzzer-pin`: GPIO pin for buzzer (default 18)
- `--led-pin`: GPIO pin for LED (default 23)
- `--gps-port`: Serial port for GPS (e.g., /dev/ttyUSB0)
- `--wifi-interface`: WiFi interface for sniffing (e.g., wlan1mon)
- `--no-ble`: Disable BLE scanning
- `--no-wifi`: Disable WiFi scanning
- `--log-dir`: Directory for log files

## Data Output
Logs are saved in the `logs/` directory.
- `*.csv`: Raw detection data.
- `*.kml`: Google Earth compatible map file (generated on exit).
