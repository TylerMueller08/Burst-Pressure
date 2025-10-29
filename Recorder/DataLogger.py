import csv
import re
import threading
import time

class DataLogger:
    def __init__(self, serialPort, csvFilename, videoLogger, interval=0.1):
        self.serialPort = serialPort
        self.videoLogger = videoLogger
        self.csvFile = open(csvFilename, mode='a', newline='')
        self.csvWriter = csv.writer(self.csvFile)
        self.interval = interval

        self.lock = threading.Lock()
        self.startTime = None
        self.stop_event = threading.Event()
        self.thread = None

        if self.csvFile.tell() == 0:
            self.csvWriter.writerow(['Elapsed [s]', 'Pressure [PSI]', 'Diameter [px]'])

    def readPressure(self):
        try:
            raw = self.serialPort.readline()
            line = raw.decode('utf-8', errors='ignore').strip()
            nums = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)]
            return nums[-1] if nums else None
        except (UnicodeDecodeError, ValueError):
            return None
        except Exception as e:
            print(f"Pressure Reading Error: {e}")
            return None

    def controlLoop(self):
        next_time = self.startTime
        while self.recording:
            now = time.perf_counter()
            elapsed = now - self.startTime

            pressure = self.readPressure()
            diameter = self.videoLogger.getLatestDiameter()

            try:
                with self.lock:
                    self.csvWriter.writerow([f"{elapsed:.3f}", pressure, diameter])
                    self.csvFile.flush()
            except Exception as e:
                print(f"DataLogger Write Error: {e}")

            next_time += self.interval
            sleep_time = next_time - time.perf_counter()

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                next_time = time.perf_counter()

    def start(self):
        self.startTime = time.perf_counter()
        self.recording = True
        self.thread = threading.Thread(target=self.controlLoop, daemon=True)
        self.thread.start()

    def stop(self, join_timeout=2.0):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=join_timeout)

        if self.thread is None or not self.thread.is_alive():
            try:
                self.csvFile.close()
            except Exception as e:
                print(f"Error closing CSV File: {e}")
        else:
            print("Warning: DataLogger thread did not stop within timeout; CSV file not closed.")