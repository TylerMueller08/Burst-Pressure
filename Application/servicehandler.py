import time
from PySide6.QtCore import QTimer, Property, QObject, Signal, Slot
from datalogger import DataLogger
from videologger import VideoLogger
from serialhandler import SerialHandler, MockSerialHandler

class ServiceHandler(QObject):
    relayStatusChanged = Signal()
    pressureStatusChanged = Signal()

    def __init__(self):
        super().__init__()
        self.relay = SerialHandler("COM5", 9600)
        self.pressure = SerialHandler("COM4", 115200)
        self.running = False

        self._relayStatus = "Relay Unknown"
        self._pressureStatus = "Pressure Unknown"

        # Connection Status Timer
        self.status = QTimer()
        self.status.setInterval(1000)
        self.status.timeout.connect(self.tryConnect)

        self.status.start()

        # Time-Based Structure
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)

        self.relay.connect()
        self.pressure.connect()

    @Slot()
    def start(self):
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
        self.relay.send('2') # Close Relays
        self.timer.stop()
        self.data_logger.stop() # Stop Pressure Logging
        self.video_logger.stop() # Stop Video Recording
        self.running = False

    def update(self):
        if self.running:
            self.data_logger.update()

    def cleanup(self):
        self.status.stop()
        self.relay.disconnect()
        self.pressure.disconnect()

    def tryConnect(self):
        if self.relay.is_connected:
            self.setRelayStatus("Relay Connected")
        else:
            self.setRelayStatus("Relay Disconnected")
            self.relay.connect()
        if self.pressure.is_connected:
            self.setPressureStatus("Pressure Connected")
        else:
            self.setPressureStatus("Pressure Disconnected")
            self.pressure.connect()

    def getRelayStatus(self):
        return self._relayStatus

    def setRelayStatus(self, value):
        if self._relayStatus != value:
            self._relayStatus = value
            self.relayStatusChanged.emit()

    relayStatus = Property(str, getRelayStatus, notify=relayStatusChanged)

    def getPressureStatus(self):
        return self._pressureStatus

    def setPressureStatus(self, value):
        if self._pressureStatus != value:
            self._pressureStatus = value
            self.pressureStatusChanged.emit()

    pressureStatus = Property(str, getPressureStatus, notify=pressureStatusChanged)
