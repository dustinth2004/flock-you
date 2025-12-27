from scapy.all import sniff, Dot11, Dot11Beacon, Dot11ProbeReq, Dot11Elt
import threading
import time
from .signatures import WIFI_SSID_PATTERNS, MAC_PREFIXES

class WiFiScanner:
    def __init__(self, interface, callback):
        self.interface = interface
        self.callback = callback
        self.running = False
        self.thread = None

    def start(self):
        if not self.interface:
            print("[WiFi] No interface specified. WiFi scanning disabled.")
            return

        print(f"[WiFi] Starting sniffer on {self.interface} (Monitor Mode required)...")
        self.running = True
        self.thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        # Scapy sniff doesn't have an easy "stop" without timeout,
        # but since it's in a daemon thread, main exit will kill it.
        # We can also use stop_filter in newer scapy.

    def _sniff_loop(self):
        try:
            sniff(iface=self.interface, prn=self._handle_packet, store=0,
                  stop_filter=lambda x: not self.running)
        except Exception as e:
            print(f"[WiFi] Sniffing error (check permissions/monitor mode): {e}")
            self.running = False

    def _handle_packet(self, packet):
        if not self.running:
            return

        if packet.haslayer(Dot11):
            frame_type = packet.type
            subtype = packet.subtype

            # 0=Management, 8=Beacon, 4=Probe Request
            if frame_type == 0 and (subtype == 8 or subtype == 4):
                rssi = 0
                # Try to get RSSI from Radiotap header
                if packet.haslayer('Radiotap'):
                    # This is platform/driver dependent
                    try:
                        rssi = packet.dbm_antsignal
                    except:
                        pass

                addr2 = packet.addr2 # Sender MAC
                if not addr2:
                    return

                # Get SSID
                ssid = ""
                try:
                    if packet.haslayer(Dot11Elt):
                        # SSID is usually the first element (ID 0)
                        elt = packet[Dot11Elt]
                        while isinstance(elt, Dot11Elt):
                            if elt.ID == 0:
                                ssid = elt.info.decode('utf-8', errors='ignore')
                                break
                            elt = elt.payload
                except:
                    pass

                # Check patterns
                self._check_and_report(addr2, ssid, rssi, subtype)

    def _check_and_report(self, mac, ssid, rssi, subtype):
        # 1. Check SSID
        is_ssid_match = False
        if ssid:
            for pattern in WIFI_SSID_PATTERNS:
                if pattern.lower() in ssid.lower():
                    is_ssid_match = True
                    break

        # 2. Check MAC Prefix
        mac_clean = mac.upper().replace(':', '')
        is_mac_match = False
        for prefix in MAC_PREFIXES:
            clean_prefix = prefix.upper().replace(':', '')
            if mac_clean.startswith(clean_prefix):
                is_mac_match = True
                break

        if is_ssid_match or is_mac_match:
            threat_score = 0
            desc = []

            if is_ssid_match and is_mac_match:
                threat_score = 100
                desc.append("Flock Safety (SSID+MAC)")
            elif is_ssid_match:
                threat_score = 85
                desc.append("Flock Safety (SSID Match)")
            elif is_mac_match:
                threat_score = 70
                desc.append("Flock Safety (MAC Match)")

            type_str = "Beacon" if subtype == 8 else "Probe Request"

            detection = {
                'timestamp': "", # filled by main
                'protocol': 'WiFi',
                'type': type_str,
                'mac': mac,
                'name': ssid,
                'rssi': rssi,
                'threat_score': threat_score,
                'description': "; ".join(desc)
            }
            self.callback(detection)
