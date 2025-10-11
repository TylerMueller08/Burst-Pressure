import time
import random

class MockSerial:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.isOpen = True
        self.pressure = 0.0
        self.increment = 1.0 # PSI per read

    @property
    def is_open(self):
        return self.isOpen

    def write(self, command):
        print(f"[MOCK] Write to {self.port}: {command}")
        if command == b'1':
            self.pressure = 0.0
        elif command == b'2':
            print("[MOCK] Stop command received.")
        
    def readline(self):
        self.pressure += self.increment + random.uniform(-0.2, 0.2)
        time.sleep(0.05)
        return f"Pressure: {self.pressure:.2f} PSI\n".encode('utf-8')
    
    def close(self):
        self.isOpen = False
        print(f"[MOCK] Closed port {self.port}")