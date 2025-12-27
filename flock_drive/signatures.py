# WiFi SSID patterns to detect (case-insensitive)
WIFI_SSID_PATTERNS = [
    "flock",        # Standard Flock Safety naming
    "Flock",        # Capitalized variant
    "FLOCK",        # All caps variant
    "FS Ext Battery", # Flock Safety Extended Battery devices
    "Penguin",      # Penguin surveillance devices
    "Pigvision"     # Pigvision surveillance systems
]

# Known Flock Safety MAC address prefixes
MAC_PREFIXES = [
    # FS Ext Battery devices
    "58:8e:81", "cc:cc:cc", "ec:1b:bd", "90:35:ea", "04:0d:84",
    "f0:82:c0", "1c:34:f1", "38:5b:44", "94:34:69", "b4:e3:f9",

    # Flock WiFi devices
    "70:c9:4e", "3c:91:80", "d8:f3:bc", "80:30:49", "14:5a:fc",
    "74:4c:a1", "08:3a:88", "9c:2f:9d", "94:08:53", "e4:aa:ea"
]

# Device name patterns for BLE advertisement detection
DEVICE_NAME_PATTERNS = [
    "FS Ext Battery",  # Flock Safety Extended Battery
    "Penguin",         # Penguin surveillance devices
    "Flock",           # Standard Flock Safety devices
    "Pigvision"        # Pigvision surveillance systems
]

# Raven Device Information Service (used across all firmware versions)
RAVEN_DEVICE_INFO_SERVICE = "0000180a-0000-1000-8000-00805f9b34fb"

# Raven GPS Location Service (firmware 1.2.0+)
RAVEN_GPS_SERVICE = "00003100-0000-1000-8000-00805f9b34fb"

# Raven Power/Battery Service (firmware 1.2.0+)
RAVEN_POWER_SERVICE = "00003200-0000-1000-8000-00805f9b34fb"

# Raven Network Status Service (firmware 1.2.0+)
RAVEN_NETWORK_SERVICE = "00003300-0000-1000-8000-00805f9b34fb"

# Raven Upload Statistics Service (firmware 1.2.0+)
RAVEN_UPLOAD_SERVICE = "00003400-0000-1000-8000-00805f9b34fb"

# Raven Error/Failure Service (firmware 1.2.0+)
RAVEN_ERROR_SERVICE = "00003500-0000-1000-8000-00805f9b34fb"

# Health Thermometer Service (firmware 1.1.7)
RAVEN_OLD_HEALTH_SERVICE = "00001809-0000-1000-8000-00805f9b34fb"

# Location and Navigation Service (firmware 1.1.7)
RAVEN_OLD_LOCATION_SERVICE = "00001819-0000-1000-8000-00805f9b34fb"

# Known Raven service UUIDs for detection
RAVEN_SERVICE_UUIDS = [
    RAVEN_DEVICE_INFO_SERVICE,
    RAVEN_GPS_SERVICE,
    RAVEN_POWER_SERVICE,
    RAVEN_NETWORK_SERVICE,
    RAVEN_UPLOAD_SERVICE,
    RAVEN_ERROR_SERVICE,
    RAVEN_OLD_HEALTH_SERVICE,
    RAVEN_OLD_LOCATION_SERVICE
]

def get_raven_service_description(uuid):
    uuid_lower = uuid.lower()
    if uuid_lower == RAVEN_DEVICE_INFO_SERVICE:
        return "Device Information (Serial, Model, Firmware)"
    if uuid_lower == RAVEN_GPS_SERVICE:
        return "GPS Location Service (Lat/Lon/Alt)"
    if uuid_lower == RAVEN_POWER_SERVICE:
        return "Power Management (Battery/Solar)"
    if uuid_lower == RAVEN_NETWORK_SERVICE:
        return "Network Status (LTE/WiFi)"
    if uuid_lower == RAVEN_UPLOAD_SERVICE:
        return "Upload Statistics Service"
    if uuid_lower == RAVEN_ERROR_SERVICE:
        return "Error/Failure Tracking Service"
    if uuid_lower == RAVEN_OLD_HEALTH_SERVICE:
        return "Health/Temperature Service (Legacy)"
    if uuid_lower == RAVEN_OLD_LOCATION_SERVICE:
        return "Location Service (Legacy)"
    return "Unknown Raven Service"

def estimate_raven_firmware_version(service_uuids):
    if not service_uuids:
        return "Unknown"

    uuids_lower = [u.lower() for u in service_uuids]

    has_new_gps = RAVEN_GPS_SERVICE.lower() in uuids_lower
    has_old_location = RAVEN_OLD_LOCATION_SERVICE.lower() in uuids_lower
    has_power_service = RAVEN_POWER_SERVICE.lower() in uuids_lower

    if has_old_location and not has_new_gps:
        return "1.1.x (Legacy)"
    if has_new_gps and not has_power_service:
        return "1.2.x"
    if has_new_gps and has_power_service:
        return "1.3.x (Latest)"

    return "Unknown Version"
