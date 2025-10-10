import os
import serial
import atexit
import signal
from video_logger import VideoLogger
from pressure_logger import PressureLogger
from utils import currentDatestamp

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(CURRENT_DIR, "Results")

os.makedirs(RESULTS_DIR, exist_ok=True)

class RecorderController:
    def __init__(self):
        self.arduino = serial.Serial('COM5', 9600, timeout=1)
        self.pressure = serial.Serial('COM4', 115200, timeout=0.2)
        self.video_logger = VideoLogger()
        self.pressure_logger = None
        self.recording = False

        # Noticed that the relay does not close upon abrupt exits.
        # This should stop the relay when it detects such exit, including Ctrl+C and termination signals.
        atexit.register(self._safe_shutdown)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def toggle(self):
        self._start_logging(currentDatestamp()) if not self.recording else self._stop_logging()

    def _start_logging(self, timestamp):
        video_path = os.path.join(RESULTS_DIR, f"Video_{timestamp}.mp4")
        pressure_path = os.path.join(RESULTS_DIR, f"Pressure_{timestamp}.csv")

        self.video_logger.start(video_path)
        self.pressure_logger = PressureLogger(self.pressure, pressure_path)
        self.pressure_logger.start()
        self._send_arduino(b'1')
        self.recording = True
        print("Started Logging at", timestamp)

    def _stop_logging(self):
        self._send_arduino(b'2')
        if self.pressure_logger:
            self.pressure_logger.stop()
        self.video_logger.stop()
        self.recording = False
        print("Stopped Logging at", currentDatestamp())

    def _send_arduino(self, command):
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(command)
            except Exception as e:
                print("Error: Cannot communicate with Arduino:", e)
        else:
            print("Error: Arduino port not open. Skipping operation.")

    def _safe_shutdown(self):
        if self.recording:
            print("Exiting safely. Shutting down all operations.")
            self._stop_logging()

    def _signal_handler(self, signum, _frame):
        print(f"Signal {signum} received. Shutting down all operations.")
        self._safe_shutdown()
        exit(0)