import serial
import pynmea2
import threading
import time
import glob

class GPSManager:
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.current_fix = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.connected = False

    def find_gps_port(self):
        """Auto-detect likely GPS ports."""
        if self.port:
            return self.port

        # Common patterns for USB GPS dongles on Linux/RPi
        patterns = ['/dev/ttyUSB*', '/dev/ttyACM*']
        for pattern in patterns:
            ports = glob.glob(pattern)
            if ports:
                print(f"[GPS] Found potential GPS port: {ports[0]}")
                return ports[0]
        return None

    def start(self):
        """Start the GPS reading thread."""
        target_port = self.find_gps_port()
        if not target_port:
            print("[GPS] No GPS port found. GPS disabled.")
            return

        self.port = target_port
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the GPS reading thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _read_loop(self):
        print(f"[GPS] Connecting to {self.port}...")
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                    self.connected = True
                    print("[GPS] Connected.")
                    while self.running:
                        try:
                            line = ser.readline().decode('ascii', errors='replace').strip()
                            if line.startswith('$G'):
                                msg = pynmea2.parse(line)
                                if isinstance(msg, (pynmea2.types.talker.GGA, pynmea2.types.talker.RMC)):
                                    # Update current fix if we have a valid fix
                                    if msg.is_valid:
                                        with self.lock:
                                            self.current_fix = msg
                        except pynmea2.ParseError:
                            continue
                        except Exception as e:
                            print(f"[GPS] Read error: {e}")
                            break
            except Exception as e:
                self.connected = False
                print(f"[GPS] Connection error: {e}. Retrying in 5s...")
                time.sleep(5)

    def get_location(self):
        """Return the current location as a dict or None."""
        with self.lock:
            if not self.current_fix:
                return None

            # Extract relevant fields depending on message type
            # GGA has altitude, RMC has speed/course
            data = {
                'latitude': self.current_fix.latitude,
                'longitude': self.current_fix.longitude,
                'timestamp': getattr(self.current_fix, 'timestamp', None),
                'altitude': getattr(self.current_fix, 'altitude', 0),
                'num_sats': getattr(self.current_fix, 'num_sats', 0),
                'gps_qual': getattr(self.current_fix, 'gps_qual', 0)
            }
            return data
