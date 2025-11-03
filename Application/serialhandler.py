import serial, random, re, utils

class SerialHandler:
    def __init__(self, port, baudrate, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            utils.log("Serial Handler", f"Successfully connect to {self.port} at {self.baudrate}")
        except Exception as e:
            utils.log("Serial Handler", f"Failed to connect to {self.port} at {self.baudrate}: {e}")

    def disconnect(self):
        if self.is_connected:
            self.connection.close()
            utils.log("Serial Handler", f"Disconnected from {self.port} at {self.baudrate}")

    def send(self, command):
        if self.is_connected:
            self.connection.write(command)
            utils.log("Serial Handler", f"Sent Command: {command}!")

    def read(self):
        if not self.is_connected:
            return None
        try:
            raw = self.connection.readline()
            line = raw.decode("utf-8", errors="ignore").strip()
            nums = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)]
            return nums[-1] if nums else None
        except Exception as e:
            utils.log("Serial Handler", f"Failed to read {self.port} at {self.baudrate}: {e}")
            return None
    
    @property
    def is_connected(self):
        return self.connection and self.connection.is_open


class MockSerialHandler:
    def connect(self):
        utils.log("Mock Serial Handler", "Connected")

    def disconnect(self):
        utils.log("Mock Serial Handler", "Disconnected")

    def send(self, command):
        utils.log("Mock Serial Handler", f"Sent Command: {command}")

    def read(self):
        return random.uniform(0.0, 16.0)
