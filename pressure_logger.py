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
    
    def start(self):
        self.recording = True
        threading.Thread(target=self._pressure_loop, daemon=True).start()

    def _pressure_loop(self):
        while self.recording:
            timestamp = currentTimestamp()
            value = None

            try:
                raw = self.serial_port.readline()
                if raw:
                    try:
                        line = raw.decode('utf-8', errors='ignore').strip()
                    except:
                        line = str(raw)

                    nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)
                    if nums:
                        try:
                            value = float(nums[-1])
                        except:
                            value = nums[-1]
            except Exception as e:
                print("Error: Pressure reading:", e)
                
            with self.lock:
                self.csv_writer.writerow([timestamp, value if value is not None else ''])
                self.csv_file.flush()

            time.sleep(0.25)

    def stop(self):
        self.recording = False
        time.sleep(0.3) # Allowing for the last write
        self.csv_file.close()
