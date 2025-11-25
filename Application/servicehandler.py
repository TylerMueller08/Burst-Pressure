import time, os, utils
from PySide6.QtCore import QTimer, QObject, Slot, Signal
from captureworker import CaptureWorker
from serialhandler import SerialHandler

class ServiceHandler(QObject):
    pressureUpdated = Signal(bool)
    relayUpdated = Signal(bool)
    connected = Signal(bool)

    def __init__(self):
        super().__init__()
        self.relay = SerialHandler("COM5", 9600)
        self.pressure = SerialHandler("COM4", 115200)

    @Slot(str)
    def start(self, prefix):
        self.relay.send("1") # Open Relays
        self.start_time = time.perf_counter()

        self.worker = CaptureWorker(
            pressure_handler = self.pressure,
            start_time = self.start_time,
            prefix = prefix,
            fps = 10)

        self.worker.start()

    @Slot()
    def stop(self):
        self.relay.send("2") # Close Relays
        
        if hasattr(self, "worker"):
            self.worker.stop()
            self.worker.wait()

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
            utils.log("Service Handler", "Failed to open Iriun Webcam. Please open the application manually for video recording.")
