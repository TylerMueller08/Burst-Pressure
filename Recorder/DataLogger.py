import csv
import re
import threading
import time

class DataLogger:
    def __init__(self, serialPort, csvFilename, videoLogger, interval=0.25):
        self.serialPort = serialPort
        self.videoLogger = videoLogger
        self.csvFile = open(csvFilename, mode='a', newline='')
        self.csvWriter = csv.writer(self.csvFile)
        self.interval = interval
        self.recording = False
        self.lock = threading.Lock()
        self.startTime = None

        if self.csvFile.tell() == 0:
            self.csvWriter.writerow(['Elapsed [s]', 'Pressure [PSI]', 'Diameter [px]'])

    def readPressure(self):
        try:
            raw = self.serialPort.readline()
            line = raw.decode('utf-8', errors='ignore').strip()
            nums = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)]
            return nums[-1] if nums else None
        except:
            return None
        
    def controlLoop(self):
        self.selfTime = time.perf_counter()
        while self.recording:
            elapsed = time.perf_counter() - self.startTime
            pressure = self.readPressure()
            diameter = self.videoLogger.getLatestDiameter()
            with self.lock:
                self.csvWriter.writerow([f"{elapsed:.3f}", pressure, diameter])
                self.csvFile.flush()
            time.sleep(self.interval)

    def start(self):
        self.startTime = time.perf_counter()
        self.recording = True
        threading.Thread(target=self.controlLoop, daemon=True).start()

    def stop(self):
        self.recording = False
        time.sleep(self.interval + 0.1)
        self.csvFile.close()
