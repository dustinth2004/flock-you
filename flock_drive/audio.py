import os
import pygame
import threading
import queue
from .assets import generate_alert_sounds, AUDIO_DIR

class AudioSystem:
    def __init__(self):
        self.enabled = False
        try:
            # Generate assets if missing
            generate_alert_sounds()

            # Init Pygame Mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True

            # Load Sounds
            self.sounds = {
                'boot': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "boot.wav")),
                'low': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "alert_low.wav")),
                'high': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "alert_high.wav")),
                'critical': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "alert_critical.wav")),
                'heartbeat': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "heartbeat.wav"))
            }
            print("[Audio] System Audio Initialized (Headphone Jack/HDMI)")
        except Exception as e:
            print(f"[Audio] Initialization Failed: {e}")
            self.enabled = False

    def play(self, sound_name):
        if not self.enabled: return
        try:
            if sound_name in self.sounds:
                self.sounds[sound_name].play()
        except Exception as e:
            print(f"[Audio] Playback Error: {e}")

    def boot_sequence(self):
        if not self.enabled: return
        self.play('boot')

    def detection_alert(self, threat_score):
        if not self.enabled: return

        if threat_score >= 90:
            self.play('critical')
        elif threat_score >= 70:
            self.play('high')
        else:
            self.play('low')

    def heartbeat(self):
        if not self.enabled: return
        self.play('heartbeat')
