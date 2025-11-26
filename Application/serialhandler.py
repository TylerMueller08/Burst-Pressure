import serial, random, re, utils

class SerialHandler:
    def __init__(self, port, baudrate, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        if not self.connection:
            try:
                self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                utils.log("Serial Handler", f"Successfully connected to {self.port} at {self.baudrate}")
            except:
                self.drop()
                utils.log("Serial Handler", f"Failed to connect to {self.port} at {self.baudrate}")

    def disconnect(self):
        if self.connection:
            self.drop()
            utils.log("Serial Handler", f"Disconnected from {self.port} at {self.baudrate}")

    def send(self, command):
        if self.is_connected:
            try:
                self.connection.write(command.encode())
                utils.log("Serial Handler", f"Sent Command: {command} to {self.port} at {self.baudrate}")
            except:
                self.drop()

    def read(self):
        if self.is_connected:
            try:
                raw = self.connection.readline()
                line = raw.decode("utf-8", errors="ignore").strip()
                nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)
                return float(nums[-1]) if nums else None
            except:
                self.drop()
                utils.log("Serial Handler", f"Failed to read {self.port} at {self.baudrate}")
                return None
        
    def drop(self):
        try:
            if self.connection:
                self.connection.close()
        except:
            pass
        self.connection = None

    @property
    def is_connected(self):
        if not self.connection or not self.connection.is_open:
            return False
        try:
            self.connection.write(b"")
            return True
        except:
            self.drop()
            return False


class MockSerialHandler:
    def __init__(self, name="Mock", should_connect=True):
        self.name = name
        self.should_connect = should_connect
        self.connected = False

    def connect(self):
        if not self.connected and self.should_connect:
            self.connected = True
            utils.log("Mock Serial Handler", f"Connected to {self.name}")

    def disconnect(self):
        if self.connected:
            self.connected = False
            utils.log("Mock Serial Handler", f"Disconnected from {self.name}")

    def send(self, command):
        if self.connected:
            utils.log("Mock Serial Handler", f"Sent Command: {command}")

    def read(self):
        if self.connected:
            return random.uniform(0.0, 16.0)
    
    @property
    def is_connected(self):
        return self.connected