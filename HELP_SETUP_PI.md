# Setup Guide: Raspberry Pi (Dedicated)

This guide walks you through setting up **Flock You** (aka Flock Drive) on a Raspberry Pi as a dedicated, always-on surveillance scanner.

## Recommended Hardware
- **Raspberry Pi**: Pi 3B+, 4, or 5 recommended.
- **Power Supply**: Official USB-C power supply or robust battery bank (3A+).
- **Storage**: 16GB+ MicroSD Card.
- **GPS**: USB GPS Dongle (e.g., VK-172, GlobalSat BU-353-S4).
- **WiFi Adapter**: External USB Adapter with **Monitor Mode** (e.g., Panda PAU09, Alfa AWUS036NHA).
- **Audio (Optional)**:
  - **Speaker**: Connect to the 3.5mm Headphone Jack.
  - **Buzzer**: Connect a Piezo Buzzer to GPIO 18 (Signal) and GND.

## 1. Operating System Setup
1. Download **Raspberry Pi Imager**.
2. Select **Raspberry Pi OS Lite (64-bit)**.
3. Configure settings (Gear Icon):
   - Hostname: `flock-you`
   - Username: `pi`
   - Enable SSH.
   - Configure WiFi: Enter your Home WiFi credentials (initially required for installation).
4. Write to SD Card.

## 2. Installation
1. SSH into the Pi: `ssh pi@flock-you.local`
2. Update: `sudo apt update && sudo apt upgrade -y`
3. Clone & Install:
   ```bash
   git clone https://github.com/colonelpanic/flock-you.git
   cd flock-you
   sudo ./install.sh
   ```
4. **Select Option 1 (Dedicated Device)**.
   - You will be asked for your **Home WiFi** SSID and Password.
   - This sets up the **"Home Base"** feature:
     - **At Home**: Connects to your WiFi -> Plays "Fancy Bong" -> Ready for upload.
     - **In Car**: Creates Hotspot `flock-you` (Pass: `flocku2`) -> Starts Scanning.

## 3. Configuration (Monitor Mode)
Edit the service file to use your external WiFi adapter (usually `wlan1` or `wlan1mon`):

```bash
sudo nano /etc/systemd/system/flockdrive.service
```

Update the `ExecStart` line:
```ini
ExecStart=/opt/flock_drive/venv/bin/python -m flock_drive.main --wifi-interface wlan1mon --gps-port /dev/ttyUSB0
```

Restart the service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart flockdrive
```

## 4. Usage

### Mobile Mode (In the Field)
1. Power on the device.
2. It will fail to find your Home WiFi and create a hotspot.
3. Connect your phone to WiFi: **`flock-you`** (Password: **`flocku2`**).
4. Open Browser: **`http://10.0.0.1:5000`**
5. Audio: You will hear a "Heartbeat" beep every 10 seconds to confirm it's running.

### Home Base Mode (Returning Home)
1. When you pull into your driveway/range of Home WiFi, the device will (eventually) switch networks.
   - *Note: You may need to reboot or wait for the auto-switcher script to cycle.*
2. **"Fancy Bong"**: You will hear a pleasant chime indicating connection.
3. Access the dashboard at **`http://flock-you.local:5000`**.
4. **Download Logs**: Click the "Export KML" button on the dashboard.
5. **View Map**: Drag the KML file into **Google Earth Pro** or **Google MyMaps** to see your patrol results.

## 5. Audio Setup
The system plays audio through **both** the 3.5mm jack and GPIO Buzzer simultaneously.

### Wiring a Buzzer
- **Positive (+)**: Pin 12 (GPIO 18)
- **Negative (-)**: Pin 14 (GND)

*(No extra configuration needed, enabled by default)*.
