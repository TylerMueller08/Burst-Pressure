import serial
import threading
import queue
import time

class SerialManager:
    def __init__(self, ports, baud=115200, data_queue=None, start_time=None):
        self.ports = ports
        self.baud = baud
        self.threads = []
        self.data_queue = data_queue or queue.Queue()
        self.start_time = start_time or time.perf_counter()
        self.running = False

    def _read_loop(self, port):
        ser = serial.Serial(port, self.baud, timeout=1)
        while self.running:
            if ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()
                timestamp = time.perf_counter() - self.start_time
                self.data_queue.put(("serial", port, timestamp, line))

    def start(self):
        self.running = True
        for port in self.ports:
            t = threading.Thread(target=self._read_loop, args=(port,), daemon=True)
            self.threads.append(t)
            t.start()

    def stop(self):
        self.running = False
        for t in self.threads:
            t.join(timeout=1)









import time
import queue
from serial_manager import SerialManager
from relay_controller import RelayController
from video_logger import VideoLogger
from data_logger import DataLogger

def fake_relay(on):
    # Replace with actual GPIO or Arduino relay control
    print(f"Relay {'ON' if on else 'OFF'}")

if __name__ == "__main__":
    data_queue = queue.Queue()
    start_time = time.perf_counter()

    serials = SerialManager(["/dev/ttyUSB0", "/dev/ttyUSB1"], data_queue=data_queue, start_time=start_time)
    relay = RelayController(fake_relay, data_queue=data_queue, start_time=start_time)
    video = VideoLogger("output.avi", data_queue=data_queue, start_time=start_time)
    logger = DataLogger("data.csv", data_queue)

    serials.start()
    relay.start()
    video.start()

    try:
        logger.run()
    except KeyboardInterrupt:
        serials.stop()
        relay.stop()
        video.stop()
