from PySide6.QtCore import QThread
import os, utils
import cv2, csv
import math

class ServiceWorker(QThread):
    def __init__(self, pressure_handler=None, start_time=None, prefix="Unlabeled", fps=10, pressure_csv=r"C:\Users\Tyler Mueller\Downloads\Example_DATA.csv"):
        super().__init__()
        self.pressure_handler = pressure_handler
        self.start_time = start_time
        self.prefix = prefix
        self.fps = fps          # desired output FPS
        self.next_time = None
        self.interval = 1.0 / fps  # seconds per frame at desired FPS
        self.running = False
        self.pressure_data = []
        self.pressure_csv = pressure_csv

        if self.pressure_csv is not None:
            self._load_csv(self.pressure_csv)

    def _load_csv(self, csv_path):
        with open(csv_path, newline="") as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.pressure_data = [(float(row[0]), float(row[1])) for row in reader]

    def start(self):
        self.running = True
        self.next_time = 0.0
        super().start()

    def run(self):
        folder = f"data/{self.prefix}_{utils.timestamp()}"
        os.makedirs(folder, exist_ok=True)

        video_file = f"{folder}/{self.prefix}_VIDEO.mp4"

        # Input video path
        input_path = r"C:\Users\Tyler Mueller\Downloads\Example_VIDEO.mp4"
        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            utils.log("Service Worker", f"Failed to open video: {input_path}")
            return

        # Original video properties
        orig_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Video writer
        out = cv2.VideoWriter(
            video_file,
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.fps,
            (width, height)
        )

        utils.log("Service Worker", f"Video Recording Started at {video_file}")
        # utils.log("Service Worker", f"CSV Recording Started at {csv_file}")

        # How many original frames to skip to hit desired FPS
        frame_interval = orig_fps / self.fps
        next_frame_idx = 0.0
        current_frame_idx = 0

        csv_idx = 0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            if current_frame_idx >= math.floor(next_frame_idx):
                if self.pressure_data and csv_idx < len(self.pressure_data):
                    elapsed_time, pressure_kpa = self.pressure_data[csv_idx]
                else:
                    pressure_kpa = 0.0  # Default if no data.

                # Overlay
                cv2.putText(frame, f"Time: {self.next_time:.1f}s", (10, height - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Pressure: {pressure_kpa:.2f}kPa", (10, height - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                out.write(frame)

                self.next_time += self.interval
                next_frame_idx += frame_interval
                csv_idx += 1

            current_frame_idx += 1

        cap.release()
        out.release()

        utils.log("Service Worker", "Recording Stopped")

    def stop(self):
        self.running = False
