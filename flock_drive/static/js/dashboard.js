document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    // DOM Elements
    const feedList = document.getElementById('feed-list');
    const radarBlips = document.getElementById('radar-blips');
    const threatBar = document.getElementById('threat-bar');
    const threatText = document.getElementById('threat-text');
    const elDetectionCount = document.getElementById('detection-count');
    const elGpsStatus = document.getElementById('gps-status');
    const elUptime = document.getElementById('uptime');

    let startTime = Date.now();
    let highestThreat = 0;
    let threatDecayTimer = null;

    // --- SOCKET HANDLERS ---

    socket.on('connect', () => {
        console.log('[System] Connected to mainframe.');
    });

    socket.on('status_update', (stats) => {
        elDetectionCount.innerText = stats.detection_count;
        elGpsStatus.innerText = stats.gps_status;
        if(stats.start_time) startTime = stats.start_time * 1000;
    });

    socket.on('gps_update', (data) => {
        elGpsStatus.innerText = `FIX [${data.lat.toFixed(4)}, ${data.lon.toFixed(4)}]`;
        elGpsStatus.style.color = 'var(--primary)';
    });

    socket.on('new_detection', (data) => {
        addFeedItem(data);
        addRadarBlip(data);
        updateThreatLevel(data.threat_score);
    });

    // --- UI FUNCTIONS ---

    function addFeedItem(data) {
        const item = document.createElement('div');
        item.className = 'feed-item';
        if (data.threat_score >= 90) item.classList.add('critical');

        const timeStr = new Date().toLocaleTimeString('en-US', {hour12: false});

        item.innerHTML = `
            <span>${timeStr}</span>
            <span>${data.protocol}</span>
            <span>${data.mac}<br><small>${data.name || 'UNKNOWN'}</small></span>
            <span>${data.rssi}dB</span>
        `;

        feedList.insertBefore(item, feedList.firstChild);

        // Limit feed size
        if (feedList.children.length > 50) {
            feedList.removeChild(feedList.lastChild);
        }
    }

    function addRadarBlip(data) {
        const blip = document.createElement('div');
        blip.className = 'blip';

        // Random position for visual effect (since RSSI isn't directional)
        // RSSI (-100 to -30) -> Distance (Center is close)
        // Map RSSI to radius (0 to 45%)
        let rssi = Math.max(-100, Math.min(-30, data.rssi));
        let distance = ((rssi + 30) / -70) * 45;

        let angle = Math.random() * 360;

        blip.style.left = `calc(50% + ${distance * Math.cos(angle * Math.PI / 180)}%)`;
        blip.style.top = `calc(50% + ${distance * Math.sin(angle * Math.PI / 180)}%)`;

        if (data.threat_score >= 90) blip.classList.add('critical');
        else if (data.threat_score < 50) blip.classList.add('safe');

        radarBlips.appendChild(blip);

        // Remove after animation
        setTimeout(() => {
            blip.remove();
        }, 3000);
    }

    function updateThreatLevel(score) {
        if (score > highestThreat) {
            highestThreat = score;
        }

        threatBar.style.width = `${highestThreat}%`;

        if (highestThreat >= 90) {
            threatText.innerText = "CRITICAL";
            threatText.style.color = "var(--accent)";
        } else if (highestThreat >= 50) {
            threatText.innerText = "ELEVATED";
            threatText.style.color = "var(--warning)";
        } else {
            threatText.innerText = "LOW";
            threatText.style.color = "var(--primary)";
        }

        // Reset decay timer
        if (threatDecayTimer) clearTimeout(threatDecayTimer);
        threatDecayTimer = setTimeout(() => {
            highestThreat = 0;
            threatBar.style.width = '0%';
            threatText.innerText = "SCANNING";
            threatText.style.color = "var(--secondary)";
        }, 5000);
    }

    // Uptime Clock
    setInterval(() => {
        const diff = Date.now() - startTime;
        const seconds = Math.floor((diff / 1000) % 60).toString().padStart(2, '0');
        const minutes = Math.floor((diff / (1000 * 60)) % 60).toString().padStart(2, '0');
        const hours = Math.floor((diff / (1000 * 60 * 60))).toString().padStart(2, '0');
        elUptime.innerText = `${hours}:${minutes}:${seconds}`;
    }, 1000);
});
