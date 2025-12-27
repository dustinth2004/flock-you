import csv
import json
import os
import time
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = os.path.join(log_dir, f"flock_drive_{self.session_id}.csv")
        self.kml_file = os.path.join(log_dir, f"flock_drive_{self.session_id}.kml")

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self._init_csv()

    def _init_csv(self):
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp', 'Protocol', 'Type', 'MAC', 'Name/SSID',
                'RSSI', 'Threat_Score', 'Latitude', 'Longitude', 'Altitude',
                'Description'
            ])

    def log_detection(self, detection):
        """
        Log a detection to CSV immediately.
        Append-only to save memory and SD card wear.
        """
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                detection.get('timestamp'),
                detection.get('protocol'),
                detection.get('type'),
                detection.get('mac'),
                detection.get('name', ''),
                detection.get('rssi'),
                detection.get('threat_score'),
                detection.get('latitude', ''),
                detection.get('longitude', ''),
                detection.get('altitude', ''),
                detection.get('description', '')
            ])

    def close(self):
        """
        Called on shutdown. Generates the KML file from the CSV data.
        """
        try:
            print(f"[Logger] Generating KML file: {self.kml_file}")
            self._generate_kml_from_csv()
        except Exception as e:
            print(f"[Logger] Failed to generate KML: {e}")

    def _generate_kml_from_csv(self):
        if not os.path.exists(self.csv_file):
            return

        kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Flock Drive Detections</name>
"""
        kml_footer = """</Document>
</kml>"""

        with open(self.kml_file, 'w') as kml_out:
            kml_out.write(kml_header)

            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    lat = row.get('Latitude')
                    lon = row.get('Longitude')
                    # Only map entries with GPS data
                    if lat and lon and lat != '' and lon != '':
                        name = row.get('Name/SSID') or "Unknown"
                        mac = row.get('MAC')
                        desc = row.get('Description')
                        alt = row.get('Altitude') or 0

                        kml_out.write(f"""
  <Placemark>
    <name>{name}</name>
    <description>{desc} (MAC: {mac})</description>
    <Point>
      <coordinates>{lon},{lat},{alt}</coordinates>
    </Point>
  </Placemark>""")

            kml_out.write(kml_footer)
