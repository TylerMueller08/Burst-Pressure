import time
from PySide6.QtCore import QTimer, QObject, Slot
from datalogger import DataLogger
from videologger import VideoLogger
from serialhandler import SerialHandler, MockSerialHandler

class ServiceHandler(QObject):
    def __init__(self):
        super().__init__()
        self.relay = MockSerialHandler() or SerialHandler("COM5", 9600)
        self.pressure = MockSerialHandler() or SerialHandler("COM4", 115200)
        self.running = False

        # Time-based Command Structure
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)

    @Slot()
    def start(self):
        self.relay.connect()
        self.pressure.connect()
        self.relay.send("1") # Open Relays

        self.start_time = time.perf_counter()

        self.data_logger = DataLogger(pressure_handler=self.pressure, start_time=self.start_time)
        self.video_logger = VideoLogger(pressure_handler=self.pressure, start_time=self.start_time)

        self.data_logger.start() # Start Pressure Logging
        self.video_logger.start() # Start Video Logging
        self.running = True
        self.timer.start()

    @Slot()
    def stop(self):
        self.relay.send("2") # Close Relays
        self.timer.stop()
        self.data_logger.stop() # Stop Pressure Logging
        self.video_logger.stop() # Stop Video Recording
        self.relay.disconnect()
        self.pressure.disconnect()
        self.running = False

    def update(self):
        if self.running:
            self.data_logger.update()