import argparse
import asyncio
import time
import signal
import sys
from datetime import datetime
from colorama import init, Fore, Style

from .gps_manager import GPSManager
from .logger import Logger
from .feedback import FeedbackSystem
from .scanner_ble import BLEScanner
from .scanner_wifi import WiFiScanner

# Initialize colorama
init(autoreset=True)

class FlockDriveApp:
    def __init__(self, args):
        self.args = args
        self.running = True

        # Components
        self.gps = GPSManager(port=args.gps_port)
        self.logger = Logger(log_dir=args.log_dir)
        self.feedback = FeedbackSystem(buzzer_pin=args.buzzer_pin, led_pin=args.led_pin)

        # Scanners
        self.ble_scanner = BLEScanner(callback=self.handle_detection)
        self.wifi_scanner = WiFiScanner(interface=args.wifi_interface, callback=self.handle_detection)

        # State
        self.last_detection_time = 0
        self.start_time = time.time()
        self.detection_count = 0

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

        # Feedback
        self.feedback.detection_alert(detection['threat_score'])

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

        # Start Subsystems
        self.feedback.boot_sequence()
        self.gps.start()

        # Start Scanners
        if not self.args.no_ble:
            await self.ble_scanner.start()

        if not self.args.no_wifi:
            self.wifi_scanner.start()

        print(Fore.GREEN + "System Active. Hunting for signals...")
        print(Fore.GREEN + "Press Ctrl+C to stop.")

        try:
            while self.running:
                # Heartbeat every 10s
                if time.time() - self.start_time > 10:
                    self.feedback.heartbeat()
                    self.start_time = time.time()

                    # Print Status Line
                    gps_status = "Fix" if self.gps.current_fix else "No Fix"
                    sys.stdout.write(f"\rStatus: Running | Detections: {self.detection_count} | GPS: {gps_status}   ")
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
        print(Fore.GREEN + "Goodbye.")

def main():
    parser = argparse.ArgumentParser(description='Flock Drive: Surveillance Device Scanner')

    # Hardware config
    parser.add_argument('--buzzer-pin', type=int, default=18, help='GPIO pin for buzzer (default: 18)')
    parser.add_argument('--led-pin', type=int, default=23, help='GPIO pin for LED (default: 23)')
    parser.add_argument('--gps-port', type=str, help='Serial port for GPS (auto-detect if empty)')
    parser.add_argument('--wifi-interface', type=str, default='wlan1', help='WiFi interface in monitor mode (default: wlan1)')

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
