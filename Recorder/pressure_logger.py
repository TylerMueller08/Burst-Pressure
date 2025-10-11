import csv
import re
import time
import threading
from utils import currentTimestamp

class PressureLogger:
    def __init__(self, serial_port, csv_filename):
        self.serial_port = serial_port
        self.csv_file = open(csv_filename, mode='a', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.lock = threading.Lock()
        self.recording = False

        if self.csv_file.tell() == 0:
            self.csv_writer.writerow(['Timestamp [hr:min:sec.ms]', 'Pressure [PSI]'])
    
    def _read_pressure(self):
        try:
            raw = self.serial_port.readline()
            line = raw.decode('utf-8', errors='ignore').strip()
            nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)
            return float(nums[-1]) if nums else None
        except:
            return None
        
    def _loop(self):
        while self.recording:
            with self.lock:
                self.csv_writer.writerow([currentTimestamp(), self._read_pressure()])
                self.csv_file.flush()
            time.sleep(0.25) # Time between updates.

    def start(self):
        self.recording = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.recording = False
        time.sleep(0.3) # Allow time for last write.
        self.csv_file.close()
