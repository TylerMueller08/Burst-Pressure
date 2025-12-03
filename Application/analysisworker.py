from PySide6.QtCore import QThread
from ultralytics import YOLO
import matplotlib.pyplot as plt
import pandas as pd
import cv2, utils

class AnalysisWorker(QThread):
    def __init__(self, csv_path, video_path):
        super().__init__()
        self.csv_path = csv_path
        self.video_path = video_path
        self.running = False
        self.diameter_history = []

        self.model = YOLO("pipe.pt")

    def start(self):
        self.running = True
        super().start()

    def run(self):
        utils.log("Analysis Worker", "Started Analysis")
        try:
            df = pd.read_csv(self.csv_path)
            utils.log("Analysis Worker", "CSV Loaded")

            vid = cv2.VideoCapture(self.video_path)
            if not vid.isOpened():
                utils.log("Analysis Worker", "Failed to open video")
                return
            
            fps = vid.get(cv2.CAP_PROP_FPS)
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

            utils.log("Analysis Worker", f"FPS: {fps}")
            utils.log("Analysis Worker", f"Resolution: {width}x{height}")
            utils.log("Analysis Worker", f"Total Frames: {total_frames}")

            output_video = self.video_path.replace(".mp4", "_PROCESSED.mp4")
            output_csv = self.csv_path.replace(".csv", "_PROCESSED.csv")

            writer = cv2.VideoWriter(
                output_video,
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (width, height)
            )

            diameter_list = []
            frame_index = 0

            while self.running:
                ret, frame = vid.read()
                if not ret:
                    break

                frame_index += 1
                
                processed_frame, diameter = self.process_frame(frame)
                writer.write(processed_frame)

                if diameter is None:
                    diameter_list.append(0)
                else:
                    diameter_list.append(diameter)

                utils.log("Analysis Worker", f"Processed Frame {frame_index}/{total_frames}")

            vid.release()
            writer.release()

            df["Diameter [px]"] = diameter_list[:len(df)]
            df.to_csv(output_csv, index=False)

            utils.log("Analysis Worker", "Analysis Completed")
            utils.log("Analysis Worker", f"Output CSV: {output_csv}")
            utils.log("Analysis Worker", f"Output Video: {output_video}")

        except Exception as e:
            utils.log("Analysis Worker", f"Error: {e}")

    def process_frame(self, frame):
        import cv2
        import numpy as np

        results = self.model(frame, verbose=False)[0]
        debug = frame.copy()

        if results.masks is None or len(results.masks) == 0:
            cv2.putText(debug, "Diameter: N/A", (425, debug.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            return debug, None

        confs = results.boxes.conf.cpu().numpy()
        best_idx = int(np.argmax(confs))
        mask = results.masks.data[best_idx].cpu().numpy().astype(np.uint8)

        kernel = np.ones((5, 5), np.uint8)
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        color = (0, 255, 255)
        overlay = debug.copy()
        overlay[mask_clean > 0] = (
            0.4 * overlay[mask_clean > 0]
            + 0.6 * np.array(color, dtype=np.uint8)
        )
        debug = overlay

        ys, xs = np.where(mask_clean > 0)
        if len(ys) == 0:
            cv2.putText(debug, "Diameter: N/A", (425, debug.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            return debug, None

        points = np.column_stack((xs, ys))
        hull = cv2.convexHull(points)

        hull_ys = hull[:, 0, 1]
        top_y = int(np.min(hull_ys))
        bot_y = int(np.max(hull_ys))
        height_raw = bot_y - top_y

        if height_raw < 5:
            cv2.putText(debug, "Diameter: N/A", (425, debug.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            return debug, None

        self.diameter_history.append(height_raw)
        if len(self.diameter_history) > 5:
            self.diameter_history.pop(0)
        height = float(np.mean(self.diameter_history))

        cv2.line(debug, (0, top_y), (debug.shape[1], top_y), (0, 255, 0), 2)
        cv2.line(debug, (0, bot_y), (debug.shape[1], bot_y), (0, 255, 0), 2)

        cv2.putText(debug, f"Diameter: {height:.1f}px", (425, debug.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return debug, height

    def stop(self):
        self.running = False
