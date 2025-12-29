import argparse
import asyncio
import time
import signal
import sys
import threading
import os
import socket
from datetime import datetime
from colorama import init, Fore, Style

from .gps_manager import GPSManager
from .logger import Logger
from .feedback import FeedbackSystem
from .audio import AudioSystem
from .scanner_ble import BLEScanner
from .scanner_wifi import WiFiScanner
from .web_server import start_server, update_detection, update_gps_status

# Initialize colorama
init(autoreset=True)

class FlockDriveApp:
    def __init__(self, args):
        self.args = args
        self.running = True
        self.home_base_mode = False

        # Components
        self.gps = GPSManager(port=args.gps_port)
        self.logger = Logger(log_dir=args.log_dir)
        self.feedback = FeedbackSystem(buzzer_pin=args.buzzer_pin, led_pin=args.led_pin)
        self.audio = AudioSystem(use_buzzer=True, buzzer_pin=args.buzzer_pin)

        # Scanners
        self.ble_scanner = BLEScanner(callback=self.handle_detection)
        self.wifi_scanner = WiFiScanner(interface=args.wifi_interface, callback=self.handle_detection)

        # State
        self.last_detection_time = 0
        self.start_time = time.time()
        self.detection_count = 0

        # Check for Home Base Mode (Environment Variable set by systemd)
        if os.environ.get('FLOCK_HOME_BASE') == '1':
            self.check_home_base_connection()

    def check_home_base_connection(self):
        """Checks if we are connected to a Home WiFi network (Home Base Mode)."""
        try:
            # Check if we have an IP address that IS NOT the Hotspot IP (10.0.0.1)
            # This is a heuristic. A better way relies on the 'autohotspot' script status,
            # but checking IP is robust enough.
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                # connect to a public DNS to find our IP
                s.connect(('8.8.8.8', 1))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()

            print(f"[System] Current IP: {ip}")

            # If we are NOT 10.0.0.1 (Hotspot default) and not localhost, we are likely on Home WiFi
            if ip != '10.0.0.1' and not ip.startswith('127.'):
                print(f"{Fore.CYAN}[System] Home Base Detected! (Connected to WiFi)")
                self.home_base_mode = True

                # Trigger Home Base Sequence
                threading.Thread(target=self.home_base_sequence, daemon=True).start()
            else:
                print(f"[System] Mobile Mode (Hotspot Active or No Connection)")
                self.home_base_mode = False

        except Exception as e:
            print(f"[System] Network check failed: {e}")

    def home_base_sequence(self):
        """Plays the fancy bong and prepares for upload."""
        time.sleep(5) # Wait for audio system to fully init
        print(f"{Fore.MAGENTA}*** HOME BASE SEQUENCE INITIATED ***")
        self.audio.home_base_connected()

        # In a real upload scenario, we would trigger the upload here.
        # For now, we ensure the logs are flushed (Logger handles this)
        # and print a message.
        print(f"{Fore.MAGENTA}>>> KML/CSV Files Ready for Export")
        print(f"{Fore.MAGENTA}>>> Access Dashboard to Download")

    def handle_detection(self, detection):
        # Add timestamp and GPS
        detection['timestamp'] = datetime.now().isoformat()

        loc = self.gps.get_location()
        if loc:
            detection['latitude'] = loc['latitude']
            detection['longitude'] = loc['longitude']
            detection['altitude'] = loc['altitude']

        # Log it
        self.logger.log_detection(detection)

        # Alerts (GPIO + Audio)
        self.feedback.detection_alert(detection['threat_score'])
        self.audio.detection_alert(detection['threat_score'])

        # Update Web UI
        update_detection(detection)

        # Update State
        self.detection_count += 1
        self.last_detection_time = time.time()

        # Console Output
        self.print_detection(detection)

    def print_detection(self, d):
        color = Fore.WHITE
        if d['threat_score'] >= 90: color = Fore.RED + Style.BRIGHT
        elif d['threat_score'] >= 70: color = Fore.YELLOW + Style.BRIGHT
        else: color = Fore.GREEN

        print(f"{color}[!] DETECTED: {d['description']}")
        print(f"    MAC: {d['mac']} | RSSI: {d['rssi']} | Name: {d['name']}")
        if 'latitude' in d:
            print(f"    GPS: {d['latitude']:.5f}, {d['longitude']:.5f}")
        print(Style.RESET_ALL)

    async def run(self):
        print(Fore.CYAN + "========================================")
        print(Fore.CYAN + "   Flock Drive - Surveillance Scanner   ")
        print(Fore.CYAN + "========================================")

        # Start Web Server (in separate thread)
        web_thread = threading.Thread(target=start_server, kwargs={'port': self.args.web_port}, daemon=True)
        web_thread.start()

        # Start Subsystems
        self.feedback.boot_sequence()
        self.audio.boot_sequence()
        self.gps.start()

        # Start Scanners
        if not self.args.no_ble:
            await self.ble_scanner.start()

        if not self.args.no_wifi:
            self.wifi_scanner.start()

        print(Fore.GREEN + "System Active. Hunting for signals...")
        print(Fore.GREEN + f"Dashboard available at http://localhost:{self.args.web_port}")
        print(Fore.GREEN + "Press Ctrl+C to stop.")

        try:
            while self.running:
                # Heartbeat every 10s
                if time.time() - self.start_time > 10:
                    # Only play heartbeat if NOT in Home Base mode (Silence at home)
                    if not self.home_base_mode:
                        self.feedback.heartbeat()
                        self.audio.heartbeat()

                    self.start_time = time.time()

                    # Update GPS Status on Dashboard
                    loc = self.gps.get_location()
                    if loc:
                        update_gps_status("FIX", loc['latitude'], loc['longitude'])
                    else:
                        update_gps_status("SEARCHING", 0, 0)

                    # Print Status Line
                    gps_status = "Fix" if self.gps.current_fix else "No Fix"
                    mode_str = "HOME BASE" if self.home_base_mode else "MOBILE"
                    sys.stdout.write(f"\rStatus: {mode_str} | Detections: {self.detection_count} | GPS: {gps_status}   ")
                    sys.stdout.flush()

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass
        finally:
            await self.shutdown()

    async def shutdown(self):
        print(f"\n{Fore.YELLOW}Shutting down...")
        await self.ble_scanner.stop()
        self.wifi_scanner.stop()
        self.gps.stop()
        self.feedback.cleanup()
        self.logger.close()
        print(Fore.GREEN + "Goodbye.")

def main():
    parser = argparse.ArgumentParser(description='Flock Drive: Surveillance Device Scanner')

    # Hardware config
    parser.add_argument('--buzzer-pin', type=int, default=18, help='GPIO pin for buzzer (default: 18)')
    parser.add_argument('--led-pin', type=int, default=23, help='GPIO pin for LED (default: 23)')
    parser.add_argument('--gps-port', type=str, help='Serial port for GPS (auto-detect if empty)')
    parser.add_argument('--wifi-interface', type=str, default='wlan1', help='WiFi interface in monitor mode (default: wlan1)')
    parser.add_argument('--web-port', type=int, default=5000, help='Port for Web Dashboard')

    # Feature flags
    parser.add_argument('--no-ble', action='store_true', help='Disable BLE scanning')
    parser.add_argument('--no-wifi', action='store_true', help='Disable WiFi scanning')
    parser.add_argument('--log-dir', type=str, default='logs', help='Directory for logs')

    args = parser.parse_args()

    app = FlockDriveApp(args)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        app.running = False

    signal.signal(signal.SIGINT, signal_handler)

    asyncio.run(app.run())

if __name__ == "__main__":
    main()
