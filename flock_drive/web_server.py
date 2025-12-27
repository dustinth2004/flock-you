from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import logging
import threading
import time

# Suppress Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flockdrive_secret'
# Changed to threading mode to be compatible with main asyncio loop
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Shared State
latest_detections = []
server_stats = {
    'start_time': time.time(),
    'detection_count': 0,
    'gps_status': 'Waiting...'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    return jsonify(server_stats)

@socketio.on('connect')
def handle_connect():
    emit('status_update', server_stats)
    emit('history_update', latest_detections)

def update_detection(detection):
    """Called by main loop to push data to frontend."""
    global latest_detections

    # Update Stats
    server_stats['detection_count'] += 1

    # Maintain History (Max 50)
    latest_detections.insert(0, detection)
    if len(latest_detections) > 50:
        latest_detections.pop()

    # Push to Frontend
    socketio.emit('new_detection', detection)
    socketio.emit('status_update', server_stats)

def update_gps_status(status, lat, lon):
    server_stats['gps_status'] = status
    socketio.emit('gps_update', {'status': status, 'lat': lat, 'lon': lon})

def start_server(host='0.0.0.0', port=5000):
    print(f"[Web] Starting Dashboard at http://{host}:{port}")
    # Using threading mode via socketio.run
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)
