from PySide6.QtCore import QThread
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2, os, utils

class AnalysisWorker(QThread):
    def __init__(self, csv_path, video_path):
        super().__init__()
        self.csv_path = csv_path
        self.video_path = video_path
        self.running = False
        self.diameter_history = []

    def start(self):
        self.running = True
        super().start()

    def run(self):
        try:
            utils.log("Analysis Worker", "Started Analysis")

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

            file_dir = os.path.dirname(self.video_path)
            processed_dir = os.path.join(file_dir, "processed")
            os.makedirs(processed_dir, exist_ok=True)

            video_name = os.path.basename(self.video_path).replace(".mp4", "_PROCESSED.mp4")
            csv_name = os.path.basename(self.csv_path).replace(".csv", "_PROCESSED.csv")

            output_video = os.path.join(processed_dir, video_name)
            output_csv = os.path.join(processed_dir, csv_name)

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

                percent_complete = (frame_index / total_frames) * 100
                utils.log("Analysis Worker", f"Processed Frame {frame_index}/{total_frames} ({percent_complete:.2f}%)")

            vid.release()
            writer.release()

            df["Diameter [px]"] = diameter_list[:len(df)]
            df["Diameter [px]"] = df["Diameter [px]"]
            df.to_csv(output_csv, index=False)

            df = pd.read_csv(output_csv)

            pressure = df["Pressure [kPa]"].astype(float)
            diameter = df["Diameter [px]"].astype(float)

            # Reference (low pressure) state.
            P0 = pressure.iloc[0]
            D0 = diameter.iloc[0]

            # Circumferential strain
            df["Strain"] = (diameter - D0) / D0

            # Hoop stress
            df["Hoop_Stress"] = pressure - P0

            df.loc[0, "Strain"] = 0.0
            df.loc[0, "Hoop_Stress"] = 0.0

            df["Strain"] = df["Strain"].rolling(window=5, min_periods=1, center=True).mean()
            df["Hoop_Stress"] = df["Hoop_Stress"].rolling(window=5, min_periods=1, center=True).mean()

            df_sorted = df.sort_values("Strain")

            plt.figure(figsize=(8, 5))
            plt.plot(df_sorted["Strain"], df_sorted["Hoop_Stress"], linewidth=2)
            plt.xlabel("Circumferential Strain (ΔD / D₀)")
            plt.ylabel("Hoop Stress Proxy (kPa)")
            plt.title("Pressure-Strain Response")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(processed_dir, "stress_strain_plot"), dpi=300)
            plt.close()

            strain_name = os.path.basename(self.csv_path).replace(".csv", "_STRAIN.csv")
            df.round(2).to_csv(os.path.join(processed_dir, strain_name), index=False)
            df.to_csv(os.path.join(processed_dir, strain_name))

            utils.log("Analysis Worker", "Analysis Completed")
            utils.log("Analysis Worker", f"Output CSV: {output_csv}")
            utils.log("Analysis Worker", f"Output Video: {output_video}")

        except Exception as e:
            utils.log("Analysis Worker", f"Error: {e}")

    def process_frame(self, frame):
        import numpy as np
        import cv2

        debug = frame.copy()

        # Convert to grayscale.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Light blur for stable edges.
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Canny settings.
        edges = cv2.Canny(blurred, 0, 85)
        height, width = edges.shape

        # Ignore the top and bottom letterbox.
        top_limit = int(0.15 * height)
        bottom_limit = int(0.85 * height)

        # Measurement columns: 10%, 50%, 90%.
        cols = [
            int(0.10 * width),
            int(0.50 * width),
            int(0.90 * width)
        ]

        diameters = []
        colors = [
            (0, 0, 0), # Left.
            (0, 0, 0), # Middle.
            (0, 0, 0)  # Right.
        ]

        # Measure each column.
        for i, col in enumerate(cols):
            col = int(np.clip(col, 0, width - 1))

            ys = np.where(edges[top_limit:bottom_limit, col] > 0)[0]
            if len(ys) < 2:
                continue

            top_y = ys[0] + top_limit
            bottom_y = ys[-1] + top_limit

            diameter = bottom_y - top_y
            diameters.append(diameter)

            # Draw scanline.
            cv2.line(debug, (col, top_limit), (col, bottom_limit), colors[i], 1)

            # Draw diameter.
            cv2.circle(debug, (col, top_y), 4, (0, 0, 255), -1)
            cv2.circle(debug, (col, bottom_y), 4, (0, 0, 255), -1)
            cv2.line(debug, (col, top_y), (col, bottom_y), colors[i], 2)

            cv2.putText(
                debug,
                f"{diameter}px",
                (col + 5, top_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                colors[i],
                1
            )

            # No detections.
            if len(diameters) == 0:
                cv2.putText(
                    debug,
                    "Diameter: N/A",
                    (420, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                return debug, None

            # Averaging & smoothing values.
            avg_diameter = float(np.mean(diameters))

            self.diameter_history.append(avg_diameter)
            if len(self.diameter_history) > 5:
                self.diameter_history.pop(0)

            smoothed_diameter = float(np.mean(self.diameter_history))

        # Draw averaged diameter.
        cv2.putText(
            debug,
            f"Diameter: {smoothed_diameter:.2f}px",
            (420, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        return debug, smoothed_diameter
        
    def stop(self):
        self.running = False
