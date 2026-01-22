import time, os, utils
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from serialhandler import SerialHandler, MockSerialHandler

class ServiceHandler(QObject):
    pressureUpdated = Signal(bool)
    relayUpdated = Signal(bool)
    connected = Signal(bool)

    def __init__(self):
        super().__init__()

        # self.relay = SerialHandler("COM5", 9600)
        # self.pressure = SerialHandler("COM4", 115200)

        self.relay = MockSerialHandler("COM5", True)
        self.pressure = MockSerialHandler("COM4", True)

        self._pressure_last = False
        self._relay_last = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connections)

    @Slot(str)
    def start(self, prefix):
        self.relay.send("1") # Open Relays
        self.start_time = time.perf_counter()

        from serviceworker import ServiceWorker
        self.worker = ServiceWorker(
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

    @Slot()
    def launch_camera(self):
        try:
            os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Iriun Webcam\Iriun Webcam.lnk")
        except:
            utils.log("Service Handler", "Failed to open Iriun Webcam. Please open the application manually for video recording.")

    @Slot()
    def connect(self):
        self.timer.start(1000)

    @Slot()
    def disconnect(self):
        self.timer.stop()
        self.relay.disconnect()
        self.pressure.disconnect()

    def check_connections(self):
        self.relay.connect()
        self.pressure.connect()

        r = self.relay.is_connected
        p = self.pressure.is_connected

        self.relayUpdated.emit(r)
        self.pressureUpdated.emit(p)
        self.connected.emit(p and r)
