from PySide6.QtCore import QThread
import os, utils
import cv2, csv

class ServiceWorker(QThread):
    def __init__(self, pressure_handler=None, start_time=None, prefix="Unlabeled", fps=10):
        super().__init__()
        self.pressure_handler = pressure_handler
        self.start_time = start_time
        self.prefix = prefix
        self.fps = fps
        self.next_time = None
        self.interval = 0.1
        self.running = False

    def start(self):
        self.running = True
        self.next_time = self.interval
        super().start()

    def run(self):
        folder = f"data/{self.prefix}_{utils.timestamp()}"
        os.makedirs(folder, exist_ok=True)

        video_file = f"{folder}/{self.prefix}_VIDEO.mp4"
        csv_file = f"{folder}/{self.prefix}_DATA.csv"
        
        csvf = open(csv_file, "w", newline="")
        writer = csv.writer(csvf)
        writer.writerow(["Elapsed Time [s]", "Pressure [PSI]"])

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            utils.log("Service Worker", "No camera found")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(
            video_file,
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.fps,
            (width, height))

        utils.log("Service Worker", f"Video Recording Started at {video_file}")
        utils.log("Service Worker", f"CSV Recording Started at {csv_file}")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            # Shared pressure
            pressure = self.pressure_handler.read()
            if pressure is None:
                pressure = 0.0

            # Overlay
            cv2.putText(frame, f"Time: {self.next_time:.1f}s", (10, frame.shape[0]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Pressure: {pressure:.2f}PSI", (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            out.write(frame)
            writer.writerow([f"{self.next_time:.1f}", f"{pressure:.2f}"])

            self.next_time += self.interval

        cap.release()
        out.release()
        csvf.close()

        utils.log("Service Worker", "Recording Stopped")

    def stop(self):
        self.running = False
