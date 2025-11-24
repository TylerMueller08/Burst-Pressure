import utils

class DataLogger:
    def __init__(self, pressure_handler=None, start_time=None):
        self.file = None
        self.writer = None
        self.next_time = None
        self.start_time = start_time
        self.pressure_handler = pressure_handler
        self.interval = 0.1
        
    def start(self, prefix):
        self.file, self.writer = utils.create_csv(prefix, ["Elapsed Time [s]", "Pressure [PSI]"])
        self.next_time = self.interval
        utils.log("Data Logger", "Recording Started")

    def update(self):
        if not self.file:
            return
        elapsed = utils.elapsed(self.start_time)
        while elapsed >= self.next_time:
            pressure = self.pressure_handler.read()
            pressure = pressure if pressure is not None else 0.0
            self.writer.writerow([f"{self.next_time:.1f}", f"{pressure:.2f}"])
            self.next_time += self.interval

    def stop(self):
        if self.file:
            self.file.close()
            utils.log("Data Logger", "Recording Stopped")
            self.file = None