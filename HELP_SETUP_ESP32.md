# Setup Guide: ESP32 Hardware (Oui-Spy)

This guide covers the firmware setup for the **Oui-Spy** standalone device, based on the **Seeed Studio XIAO ESP32S3**.

## Hardware
- **Microcontroller**: Seeed Studio XIAO ESP32S3 (Sense or Standard).
- **Buzzer**: Passive/Active Piezo Buzzer (3V).
- **Wiring**:
  - Buzzer Positive (+) -> **GPIO 3 (D2)**
  - Buzzer Negative (-) -> **GND**

## Installation (Firmware)

### Prerequisites
- [VS Code](https://code.visualstudio.com/)
- [PlatformIO Extension](https://platformio.org/install/ide?install=vscode) for VS Code.

### Steps
1. **Open Project**: Open the `flock-you` folder in VS Code.
2. **Connect Device**: Plug your XIAO ESP32S3 into USB.
3. **Build & Upload**:
   - Click the PlatformIO Alien icon on the left sidebar.
   - Select the `xiao-esp32-s3` environment.
   - Click **Upload**.

### Verification
- **Boot Sound**: On successful boot, you should hear a "Low -> High" chirp sequence.
- **Serial Monitor**: Open the Serial Monitor (plug icon) to see debug output. You should see "Hunting for Flock Safety devices...".

## Companion Dashboard (Optional)
The ESP32 device works standalone (audio alerts), but you can view detections on a PC using the Python API dashboard.

1. **Install Dashboard**:
   ```bash
   cd api
   pip install -r requirements.txt
   ```
2. **Run Dashboard**:
   ```bash
   python flockyou.py
   ```
3. **View**: Open `http://localhost:5000`.
   - Connect the ESP32 via USB.
   - The Python script reads the Serial JSON output from the ESP32 and visualizes it.

## Troubleshooting
- **Upload Failed**: Hold the "Boot" button on the Xiao while plugging it in to enter Bootloader mode.
- **No Audio**: Check polarity of the buzzer.
