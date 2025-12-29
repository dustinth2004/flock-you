#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}
  ______ _            _      __     __
 |  ____| |          | |     \ \   / /
 | |__  | | ___   ___| | __   \ \_/ /__  _   _
 |  __| | |/ _ \ / __| |/ /    \   / _ \| | | |
 | |    | | (_) | (__|   <      | | (_) | |_| |
 |_|    |_|\___/ \___|_|\_\     |_|\___/ \__,_|

      Surveillance Device Scanner - Installer
${NC}"

# Check for root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run as root (sudo ./install.sh)${NC}"
  exit
fi

# Interactive Menu
echo "Select Installation Type:"
echo "1) Dedicated Device (Raspberry Pi / Headless)"
echo "   - Installs as Systemd Service (Auto-start on boot)"
echo "   - Sets Hostname to 'flock-you'"
echo "   - Configures Auto-Hotspot (Home WiFi / AP)"
echo "2) Personal Computer (Laptop / Desktop)"
echo "   - Installs dependencies and tools"
echo "   - Creates 'flock-you' launch command"
echo "   - No auto-start (Manual run)"
read -p "Enter choice [1/2]: " INSTALL_TYPE

if [[ "$INSTALL_TYPE" != "1" && "$INSTALL_TYPE" != "2" ]]; then
    echo -e "${RED}Invalid selection. Exiting.${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Installing System Dependencies...${NC}"
apt-get update
# Core dependencies
apt-get install -y python3-pip python3-venv libglib2.0-dev git libsdl2-dev espeak

# GPS and WiFi tools
apt-get install -y gpsd gpsd-clients aircrack-ng wireless-tools hostapd dnsmasq iw

# Install Directory
INSTALL_DIR="/opt/flock_drive"
echo -e "${GREEN}[+] Installing to $INSTALL_DIR...${NC}"

mkdir -p $INSTALL_DIR
# Copy application files
cp -r flock_drive $INSTALL_DIR/

# Check for datasets
if [ -d "datasets" ]; then
    echo -e "${GREEN}[+] Installing datasets...${NC}"
    cp -r datasets $INSTALL_DIR/
else
    echo -e "${YELLOW}[!] Warning: 'datasets' directory not found. Scanner will rely on built-in signatures only.${NC}"
fi

cp setup.py $INSTALL_DIR/ 2>/dev/null || true

# Setup Virtual Environment
echo -e "${GREEN}[+] Setting up Python Virtual Environment...${NC}"
cd $INSTALL_DIR
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install Python Requirements
echo -e "${GREEN}[+] Installing Python Dependencies...${NC}"
pip install --upgrade pip
pip install -r flock_drive/requirements.txt

# --- Branching Logic ---

if [ "$INSTALL_TYPE" == "1" ]; then
    # === Dedicated Device Setup ===
    echo -e "${GREEN}[+] Configuring Dedicated Device...${NC}"

    # 1. Hostname
    echo -e "${GREEN}[+] Setting Hostname to 'flock-you'...${NC}"
    hostnamectl set-hostname flock-you
    sed -i 's/127.0.1.1.*/127.0.1.1\tflock-you/g' /etc/hosts

    # 2. Network Configuration (Auto-Hotspot)
    echo -e "${YELLOW}--- Home Base Configuration ---${NC}"
    read -p "Enter your Home WiFi SSID (Leave empty to skip): " HOME_SSID
    if [ ! -z "$HOME_SSID" ]; then
        read -s -p "Enter your Home WiFi Password: " HOME_PASS
        echo ""

        # Create wpa_supplicant entry
        cat >> /etc/wpa_supplicant/wpa_supplicant.conf <<EOF

network={
    ssid="$HOME_SSID"
    psk="$HOME_PASS"
    priority=100
}
EOF
        echo -e "${GREEN}[+] Added '$HOME_SSID' to known networks.${NC}"
    fi

    # Install Auto-Hotspot Script (Simplified Logic)
    # Checks for connection, if none, starts AP
    echo -e "${GREEN}[+] Installing Auto-Hotspot logic...${NC}"

    # Install hostapd config for 'flock-you' / 'flocku2'
    cat > /etc/hostapd/hostapd.conf <<EOF
interface=wlan0
driver=nl80211
ssid=flock-you
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=flocku2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

    # Install dnsmasq config (DHCP Server)
    # This is critical for devices to get an IP when connecting to the hotspot
    cat > /etc/dnsmasq.conf <<EOF
interface=wlan0
dhcp-range=10.0.0.2,10.0.0.20,255.255.255.0,24h
domain=wlan
address=/flock-you.local/10.0.0.1
EOF

    # Disable hostapd/dnsmasq on boot (controlled by script)
    systemctl unmask hostapd
    systemctl disable hostapd
    systemctl disable dnsmasq

    # Create the Autoconnect Script
    cat > /usr/local/bin/autohotspot <<'EOF'
#!/bin/bash
# Checks for WiFi connection. If fails, starts Hotspot.

# Try to connect to known networks
wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
sleep 15

# Check if we have an IP
if ! wpa_cli -i wlan0 status | grep -q "ip_address"; then
    echo "No connection found. Starting Hotspot 'flock-you'..."
    killall wpa_supplicant

    # Configure Static IP for Hotspot (Modern 'ip' command)
    ip addr flush dev wlan0
    ip addr add 10.0.0.1/24 dev wlan0
    ip link set wlan0 up

    systemctl start dnsmasq
    systemctl start hostapd
else
    echo "Connected to WiFi. Mode: Home Base."
fi
EOF
    chmod +x /usr/local/bin/autohotspot

    # Add to crontab or rc.local? Use a service for reliability.
    cat > /etc/systemd/system/autohotspot.service <<EOF
[Unit]
Description=Auto Hotspot/WiFi Switcher
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/autohotspot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    systemctl enable autohotspot

    # 3. Flock Drive Service
    echo -e "${GREEN}[+] Configuring Flock Drive Service...${NC}"
    cat > /etc/systemd/system/flockdrive.service <<EOL
[Unit]
Description=Flock You Surveillance Scanner
After=autohotspot.service sound.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python -m flock_drive.main
Restart=always
RestartSec=5
Environment=SDL_AUDIODRIVER=alsa
Environment=FLOCK_HOME_BASE=1

[Install]
WantedBy=multi-user.target
EOL

    systemctl daemon-reload
    systemctl enable flockdrive
    echo -e "${GREEN}[+] Services enabled.${NC}"

    echo -e "${BLUE}=== Installation Complete (Dedicated Mode) ===${NC}"
    echo "Hostname:       flock-you"
    echo "Hotspot SSID:   flock-you"
    echo "Hotspot Pass:   flocku2"
    echo "Dashboard:      http://flock-you.local:5000"
    echo "NOTE: Reboot required for Hostname/Network changes to take effect."
    echo "Command: sudo reboot"

else
    # === PC Setup ===
    echo -e "${GREEN}[+] Configuring User Command (PC Mode)...${NC}"

    # Create a launcher script in /usr/local/bin
    cat > /usr/local/bin/flock-you <<EOL
#!/bin/bash
if [ "\$EUID" -ne 0 ]; then
  echo "Error: flock-you requires root privileges for hardware access."
  echo "Try: sudo flock-you"
  exit 1
fi

cd $INSTALL_DIR
source venv/bin/activate
echo "Starting Flock You Scanner..."
python -m flock_drive.main "\$@"
EOL

    chmod +x /usr/local/bin/flock-you

    echo -e "${BLUE}=== Installation Complete (PC Mode) ===${NC}"
    echo "Start Scanner:  sudo flock-you"
    echo "Dashboard:      http://localhost:5000"
    echo "Options:        sudo flock-you --help"
fi

echo -e "${YELLOW}
NOTE: For WiFi scanning, ensure your adapter is in Monitor Mode.
Example:
  sudo airmon-ng start wlan1
  sudo flock-you --wifi-interface wlan1mon
${NC}"
