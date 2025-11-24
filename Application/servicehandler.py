import time, os, utils
from PySide6.QtCore import QTimer, QObject, Slot, Signal
from datalogger import DataLogger
from videologger import VideoLogger
from serialhandler import SerialHandler, MockSerialHandler

class ServiceHandler(QObject):
    pressureUpdated = Signal(bool)
    relayUpdated = Signal(bool)
    connected = Signal(bool)

    def __init__(self):
        super().__init__()
        self.relay = SerialHandler("COM5", 9600)
        self.pressure = SerialHandler("COM4", 115200)
        self.running = False

        # Time-Based Structure
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)

    @Slot(str)
    def start(self, prefix):
        self.relay.send("1") # Open Relays

        self.start_time = time.perf_counter()

        self.data_logger = DataLogger(pressure_handler=self.pressure, start_time=self.start_time)
        self.video_logger = VideoLogger(pressure_handler=self.pressure, start_time=self.start_time)

        self.data_logger.start(prefix) # Start Pressure Logging
        self.video_logger.start(prefix) # Start Video Logging
        self.running = True
        self.timer.start()

    @Slot()
    def stop(self):
        self.relay.send('2') # Close Relays
        self.timer.stop()
        self.data_logger.stop() # Stop Pressure Logging
        self.video_logger.stop() # Stop Video Recording
        self.running = False

    def update(self):
        if self.running:
            self.data_logger.update()

    def connect(self):
        for device in (self.relay, self.pressure):
            if not device.is_connected:
                device.connect()

    def disconnect(self):
        for device in (self.relay, self.pressure):
            if device.is_connected:
                device.disconnect()

    @Slot()
    def reconnect(self):
        self.disconnect()
        self.connect()
        self.pressureUpdated.emit(self.pressure.is_connected)
        self.relayUpdated.emit(self.relay.is_connected)
        self.connected.emit(self.pressure.is_connected and self.relay.is_connected)

    @Slot()
    def launchCamera(self):
        try:
            os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Iriun Webcam\Iriun Webcam.lnk")
        except:
            utils.warn("Service Handler", "Failed to open Iriun Webcam. Please open the application manually for video recording.")
