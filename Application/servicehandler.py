import time
from PySide6.QtCore import QTimer, QObject, Slot, Signal
from datalogger import DataLogger
from videologger import VideoLogger
from serialhandler import SerialHandler, MockSerialHandler

class ServiceHandler(QObject):
    connectionIndicator = Signal()

    def __init__(self):
        super().__init__()
        self.relay = SerialHandler("COM5", 9600)
        self.pressure = SerialHandler("COM4", 115200)
        self.running = False

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
        self.relay.disconnect()
        self.pressure.disconnect()

    @Slot()
    def reconnect(self):
        for device in (self.relay, self.pressure):
            if device.is_connected:
                device.disconnect()
            device.connect()

        self.connectionIndicator.emit()

    @Slot(result=bool)
    def pressure_connected(self) -> bool:
        return self.pressure.is_connected

    @Slot(result=bool)
    def relay_connected(self) -> bool:
        return self.relay.is_connected