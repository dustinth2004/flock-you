import os
import wave
import math
import struct
import random

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

def ensure_audio_dir():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

def generate_tone(filename, freq_start, duration, freq_end=None, volume=0.5, type='sine'):
    """Generates a tone. If freq_end is provided, creates a sweep (chirp)."""
    ensure_audio_dir()
    filepath = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(filepath):
        return filepath

    sample_rate = 44100
    n_samples = int(sample_rate * duration)

    with wave.open(filepath, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)

        for i in range(n_samples):
            t = float(i) / sample_rate

            # Frequency calculation (Static or Sweep)
            if freq_end:
                # Linear chirp
                freq = freq_start + (freq_end - freq_start) * (t / duration)
            else:
                freq = freq_start

            if type == 'sine':
                value = math.sin(2.0 * math.pi * freq * t)
            elif type == 'square':
                value = 1.0 if math.sin(2.0 * math.pi * freq * t) > 0 else -1.0
            elif type == 'saw':
                value = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            elif type == 'tri':
                value = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0

            # Apply simple envelope (attack/decay) to avoid clicking
            envelope = 1.0
            if t < 0.05: envelope = t / 0.05
            elif t > duration - 0.05: envelope = (duration - t) / 0.05

            data = int(value * volume * envelope * 32767.0)
            w.writeframes(struct.pack('<h', data))

    return filepath

def generate_alert_sounds():
    """Generates a set of tactical alert sounds."""
    print("[Assets] Generating audio assets...")

    # 1. Boot Sound (Rising Sci-Fi Swell)
    generate_tone("boot.wav", 220, 0.6, freq_end=880, type='sine')

    # 2. Low Threat (Sonar Ping)
    generate_tone("alert_low.wav", 800, 0.1, type='sine')

    # 3. High Threat (Fast Square Wave)
    generate_tone("alert_high.wav", 1200, 0.15, type='square')

    # 4. Critical Threat (Raven) - Alarm
    generate_tone("alert_critical.wav", 2000, 0.2, type='saw')

    # 5. Heartbeat (Low Thud)
    generate_tone("heartbeat.wav", 100, 0.08, volume=0.8, type='sine')

    # 6. Home Base "Bong" (Low, resonant chime)
    # Using a triangle wave with a slight frequency drop creates a nice chime effect
    generate_tone("bong.wav", 440, 1.5, freq_end=430, volume=0.7, type='tri')

    print("[Assets] Audio generation complete.")

if __name__ == "__main__":
    generate_alert_sounds()
