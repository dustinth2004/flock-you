import time
import threading
import queue
import sys
try:
    from gpiozero import PWMOutputDevice, LED
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("[Feedback] gpiozero not found. GPIO feedback disabled.")

class FeedbackSystem:
    def __init__(self, buzzer_pin=18, led_pin=23):
        self.buzzer_pin = buzzer_pin
        self.led_pin = led_pin
        self.buzzer = None
        self.led = None

        self.queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)

        if GPIO_AVAILABLE:
            try:
                # Use PWMOutputDevice for variable frequency buzzer
                self.buzzer = PWMOutputDevice(buzzer_pin, initial_value=0.0, frequency=1000)
                self.led = LED(led_pin)
                print(f"[Feedback] GPIO initialized (Buzzer: {buzzer_pin}, LED: {led_pin})")
            except Exception as e:
                print(f"[Feedback] GPIO Init Error: {e}")
                self.buzzer = None
                self.led = None

        # Start worker thread
        self.worker_thread.start()

    def _worker(self):
        """Background thread to process beep tasks without blocking main loop."""
        while self.running:
            try:
                # Get task from queue with timeout to allow checking self.running
                task = self.queue.get(timeout=1.0)
                frequency, duration, count = task
                self._execute_beep(frequency, duration, count)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Feedback] Worker Error: {e}")

    def _execute_beep(self, frequency, duration, count):
        """Blocking beep implementation called by worker."""
        if not self.buzzer:
            # Fallback for non-GPIO devices
            print(f"\a[BEEP] {count}x {frequency}Hz") # \a is system bell
            return

        try:
            self.buzzer.frequency = frequency
            for _ in range(count):
                if not self.running: break

                self.buzzer.value = 0.5  # 50% duty cycle
                if self.led: self.led.on()
                time.sleep(duration)

                self.buzzer.value = 0.0
                if self.led: self.led.off()

                if count > 1:
                    time.sleep(0.05)
        except Exception as e:
            print(f"[Feedback] Hardware Error: {e}")

    def beep(self, frequency=1000, duration=0.1, count=1):
        """
        Enqueue a beep task. Non-blocking.
        """
        self.queue.put((frequency, duration, count))

    def boot_sequence(self):
        print("[Feedback] Queuing boot sequence...")
        self.beep(200, 0.3)
        self.beep(800, 0.3)

    def detection_alert(self, threat_score):
        """
        Play alert based on threat score.
        Higher score = higher pitch/faster.
        """
        if threat_score >= 90:
            # Critical (Raven/Definite Match)
            self.beep(2000, 0.1, 4)
        elif threat_score >= 70:
            # High
            self.beep(1500, 0.15, 3)
        else:
            # Medium/Low
            self.beep(1000, 0.2, 2)

    def heartbeat(self):
        """Periodic pulse to show system is running."""
        self.beep(600, 0.05, 1)

    def cleanup(self):
        self.running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)

        if self.buzzer:
            self.buzzer.close()
        if self.led:
            self.led.close()
