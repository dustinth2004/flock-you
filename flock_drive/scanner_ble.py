import asyncio
from bleak import BleakScanner
from .signatures import MAC_PREFIXES, DEVICE_NAME_PATTERNS, RAVEN_SERVICE_UUIDS, get_raven_service_description, estimate_raven_firmware_version

class BLEScanner:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.scanner = None

    async def start(self):
        self.running = True
        self.scanner = BleakScanner(detection_callback=self._handle_device)
        await self.scanner.start()
        print("[BLE] Scanner started.")

    async def stop(self):
        self.running = False
        if self.scanner:
            await self.scanner.stop()
        print("[BLE] Scanner stopped.")

    def _handle_device(self, device, advertisement_data):
        # 1. Check MAC Prefix
        mac = device.address.upper()
        mac_clean = mac.replace(':', '').replace('-', '')
        is_mac_match = False

        # MAC_PREFIXES are like "58:8e:81", we need to normalize check
        for prefix in MAC_PREFIXES:
            clean_prefix = prefix.upper().replace(':', '')
            if mac_clean.startswith(clean_prefix):
                is_mac_match = True
                break

        # 2. Check Device Name
        name = device.name or advertisement_data.local_name or ""
        is_name_match = False
        if name:
            for pattern in DEVICE_NAME_PATTERNS:
                if pattern.lower() in name.lower():
                    is_name_match = True
                    break

        # 3. Check Service UUIDs (Raven)
        is_raven = False
        raven_services = []
        if advertisement_data.service_uuids:
            for uuid in advertisement_data.service_uuids:
                if uuid.lower() in [u.lower() for u in RAVEN_SERVICE_UUIDS]:
                    is_raven = True
                    raven_services.append(uuid)

        # 4. Construct Detection Object if matched
        if is_mac_match or is_name_match or is_raven:
            threat_score = 0
            desc = []

            if is_raven:
                threat_score = 100
                desc.append("Raven Gunshot Detector")
                for uuid in raven_services:
                    desc.append(get_raven_service_description(uuid))
            elif is_mac_match and is_name_match:
                threat_score = 100
                desc.append("Flock Safety (MAC+Name Match)")
            elif is_mac_match:
                threat_score = 85
                desc.append("Flock Safety (MAC Match)")
            elif is_name_match:
                threat_score = 70
                desc.append("Flock Safety (Name Match)")

            detection = {
                'timestamp': "", # filled by main loop
                'protocol': 'BLE',
                'type': 'Advertisement',
                'mac': mac,
                'name': name,
                'rssi': device.rssi,
                'threat_score': threat_score,
                'description': "; ".join(desc)
            }

            # Send to main callback
            self.callback(detection)
