import os
import atexit
import signal
from VideoLogger import VideoLogger
from DataLogger import DataLogger
from Utils import currentDatestamp

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(CURRENT_DIR, "Data")
os.makedirs(RESULTS_DIR, exist_ok=True)

USE_MOCK_SERIAL = False

if USE_MOCK_SERIAL:
    from MockSerial import MockSerial
else:
    import serial

class RecorderController:
    def __init__(self):
        if USE_MOCK_SERIAL:
            self.arduino = MockSerial("COM5", 9600)
            self.pressure = MockSerial("COM4", 115200)
        else:
            self.arduino = serial.Serial("COM5", 9600, timeout=0.5)
            self.pressure = serial.Serial("COM4", 115200, timeout=0.05)

        self.videoLogger = VideoLogger()
        self.dataLogger = None
        self.recording = False

        atexit.register(self.safeShutdown)
        signal.signal(signal.SIGINT, self.signalHandler)
        signal.signal(signal.SIGTERM, self.signalHandler)

    def toggle(self):
        if not self.recording:
            self.startLogging(currentDatestamp())
        else:
            self.stopLogging(currentDatestamp())

    def startLogging(self, timestamp):
        videoPath = os.path.join(RESULTS_DIR, f"Video_{timestamp}.mp4")
        dataPath = os.path.join(RESULTS_DIR, f"Data_{timestamp}.csv")

        self.videoLogger.start(videoPath)
        self.dataLogger = DataLogger(self.pressure, dataPath, self.videoLogger, interval=0.1)
        self.dataLogger.start()
        self.sendArduino(b'1')
        self.recording = True
        print(f"Successfully started recording at {timestamp}")

    def stopLogging(self, timestamp):
        self.sendArduino(b'2')
        if self.dataLogger:
            self.dataLogger.stop(join_timeout=2.0)
        self.videoLogger.stop(join_timeout=2.0)
        self.recording = False
        print(f"Successfully stopped recording at {timestamp}")

    def sendArduino(self, command):
        if self.arduino and getattr(self.arduino, "is_open", True):
            try:
                self.arduino.write(command)
            except Exception as e:
                print(f"Error: cannot communciate with Arduino: {e}")
        else:
            print("Error: Arduino port not open. Skipping operation.")

    def safeShutdown(self):
        if self.recording:
            print("Exiting safely. Shutting down all operations . . .")
            self.stopLogging(currentDatestamp())
        try:
            if getattr(self.arduino, "is_open", False):
                self.arduino.close()
        except Exception as e:
            print(f"Error closing arduino: {e}")
        try:
            if getattr(self.pressure, "is_open", False):
                self.pressure.close()
        except Exception as e:
            print(f"Error closing pressure serial: {e}")

    def signalHandler(self, signum, _frame):
        print(f"Signal {signum} received. Shutting down all operations . . .")
        self.safeShutdown()
        exit(0)