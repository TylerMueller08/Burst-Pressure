import serial, re, utils

class SerialHandler:
    def __init__(self, port, baudrate, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            utils.log("Serial Handler", f"Successfully connected to {self.port} at {self.baudrate}")
        except Exception as e:
            utils.log("Serial Handler", f"Failed to connect to {self.port} at {self.baudrate}")

    def disconnect(self):
        if self.is_connected:
            self.connection.close()
            utils.log("Serial Handler", f"Disconnected from {self.port} at {self.baudrate}")

    def send(self, command):
        if self.is_connected:
            self.connection.write(command.encode())
            utils.log("Serial Handler", f"Sent Command: {command} to {self.port} at {self.baudrate}")

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
        if not self.connection:
            return False
        try:
            self.connection.read(1)
            return True
        except Exception:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
            return False
