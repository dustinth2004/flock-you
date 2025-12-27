#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Flock Drive Installer ===${NC}"

# Check for root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install.sh)"
  exit
fi

echo -e "${GREEN}[+] Installing System Dependencies...${NC}"
apt-get update
apt-get install -y python3-pip python3-venv libglib2.0-dev git gpsd gpsd-clients

# WiFi Monitor Mode tools (optional but useful)
apt-get install -y aircrack-ng wireless-tools

# Create Directory
INSTALL_DIR="/opt/flock_drive"
echo -e "${GREEN}[+] Installing to $INSTALL_DIR...${NC}"

mkdir -p $INSTALL_DIR
cp -r flock_drive $INSTALL_DIR/
cp -r datasets $INSTALL_DIR/  # Copy datasets if needed later
cp setup.py $INSTALL_DIR/ 2>/dev/null || true

# Setup Virtual Environment
echo -e "${GREEN}[+] Setting up Python Virtual Environment...${NC}"
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate

# Install Python Requirements
pip install -r flock_drive/requirements.txt

# Create Service File
echo -e "${GREEN}[+] Creating Systemd Service...${NC}"
cat > /etc/systemd/system/flockdrive.service <<EOL
[Unit]
Description=Flock Drive Surveillance Scanner
After=network.target bluetooth.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python -m flock_drive.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Reload Daemons
systemctl daemon-reload

echo -e "${BLUE}=== Installation Complete ===${NC}"
echo "To start the service: sudo systemctl start flockdrive"
echo "To enable on boot: sudo systemctl enable flockdrive"
echo "To view logs: sudo journalctl -u flockdrive -f"
echo ""
echo "NOTE: Ensure your WiFi adapter is in Monitor Mode if using WiFi scanning."
echo "You may need to edit /etc/systemd/system/flockdrive.service to add args (e.g., --wifi-interface wlan1mon)"
