import os
import pygame
import threading
import time
import queue

# Try importing gpiozero, but don't fail if not present (PC support)
try:
    from gpiozero import TonalBuzzer
    from gpiozero.tones import Tone
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

from .assets import generate_alert_sounds, AUDIO_DIR

class AudioSystem:
    def __init__(self, use_buzzer=False, buzzer_pin=18):
        self.system_audio_enabled = False
        self.buzzer_enabled = False
        self.buzzer = None

        # --- 1. System Audio (Jack/HDMI) Setup ---
        try:
            generate_alert_sounds()
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.system_audio_enabled = True

            self.sounds = {
                'boot': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "boot.wav")),
                'bong': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "bong.wav")), # New Fancy Bong
                'low': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "alert_low.wav")),
                'high': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "alert_high.wav")),
                'critical': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "alert_critical.wav")),
                'heartbeat': pygame.mixer.Sound(os.path.join(AUDIO_DIR, "heartbeat.wav"))
            }
            print("[Audio] System Audio Initialized (Headphone Jack/HDMI)")
        except Exception as e:
            print(f"[Audio] System Audio Init Failed: {e}")
            self.system_audio_enabled = False

        # --- 2. GPIO Buzzer Setup ---
        if use_buzzer:
            if GPIO_AVAILABLE:
                try:
                    self.buzzer = TonalBuzzer(buzzer_pin)
                    self.buzzer_enabled = True
                    print(f"[Audio] GPIO Buzzer Initialized on Pin {buzzer_pin}")
                except Exception as e:
                    print(f"[Audio] GPIO Buzzer Init Failed: {e}")
            else:
                print("[Audio] gpiozero not found, buzzer disabled.")

    def play(self, sound_name):
        # Play System Audio
        if self.system_audio_enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass

        # Play Buzzer Tone (Simulated)
        if self.buzzer_enabled:
            threading.Thread(target=self._play_buzzer_tone, args=(sound_name,), daemon=True).start()

    def _play_buzzer_tone(self, sound_name):
        """Simulate the WAV sounds with simple Tones for the buzzer"""
        if not self.buzzer: return

        try:
            if sound_name == 'boot':
                self.buzzer.play(Tone("C5"))
                time.sleep(0.1)
                self.buzzer.play(Tone("E5"))
                time.sleep(0.1)
                self.buzzer.stop()
            elif sound_name == 'bong':
                self.buzzer.play(Tone("G4"))
                time.sleep(0.5)
                self.buzzer.stop()
            elif sound_name == 'critical':
                for _ in range(3):
                    self.buzzer.play(Tone("A5"))
                    time.sleep(0.1)
                    self.buzzer.stop()
                    time.sleep(0.05)
            elif sound_name == 'high':
                self.buzzer.play(Tone("A5"))
                time.sleep(0.2)
                self.buzzer.stop()
            elif sound_name == 'low':
                self.buzzer.play(Tone("C5"))
                time.sleep(0.2)
                self.buzzer.stop()
            elif sound_name == 'heartbeat':
                self.buzzer.play(Tone("C4"))
                time.sleep(0.05)
                self.buzzer.stop()
        except Exception:
            pass # Buzzer errors shouldn't crash app

    def boot_sequence(self):
        self.play('boot')

    def home_base_connected(self):
        """Play the Fancy Bong when Home Base is reached"""
        self.play('bong')

    def detection_alert(self, threat_score):
        if threat_score >= 90:
            self.play('critical')
        elif threat_score >= 70:
            self.play('high')
        else:
            self.play('low')

    def heartbeat(self):
        self.play('heartbeat')
