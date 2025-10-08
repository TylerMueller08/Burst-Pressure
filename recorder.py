import serial
import atexit
import signal
from video_logger import VideoLogger
from pressure_logger import PressureLogger
from utils import currentDatestamp

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
        if self.recording:
            self.stop()
        else:
            self.start()

    def start(self):
        timestamp = currentDatestamp()
        self.video_logger.start(f"C:/Users/Mol/Desktop/Burst Pressure/Burst Pressure Code/Results/Unlabeled-Recording_{timestamp}.mp4")
        self.pressure_logger = PressureLogger(self.pressure, f"C:/Users/Mols/Desktop/Burst Pressure/Burst Pressure Code/Results/Unlabeled-PressureLog_{timestamp}.csv")
        self.pressure_logger.start()

        self._send_arduino_start()
        self.recording = True
        print("Started Logging at", currentDatestamp())

    def stop(self):
        self.video_logger.stop()
        if self.pressure_logger:
            self.pressure_logger.stop()

        self._send_arduino_stop()
        self.recording = False
        print("Stopped Logging at", currentDatestamp())

    def _send_arduino_start(self):
        try:
            self.arduino.write(b'1')
        except Exception as e:
            print("Error: Cannot send start to Arduino:", e)

    def _send_arduino_stop(self):
        try:
            self.arduino.write(b'2')
        except Exception as e:
            print("Error: Cannot send start to Arduino:", e)

    def _safe_shutdown(self):
        if self.recording:
            print("Program exiting. Stopping recording and relays...")
            self.stop()

    def _signal_handler(self, signum, frame):
        print(f"Signal {signum} received. Exiting safely...")
        self._safe_shutdown()
        exit(0)