from PySide6.QtCore import QThread
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2, os, utils, warnings

class AnalysisWorker(QThread):
    def __init__(self, csv_path, video_path):
        super().__init__()
        self.csv_path = csv_path
        self.video_path = video_path
        self.running = False
        self.diameter_history = []
        warnings.filterwarnings("ignore")

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

            video_name = os.path.basename(self.video_path).replace(".mp4", "_Processed.mp4")
            csv_name = os.path.basename(self.csv_path).replace(".csv", "_Processed.csv")
            combined_video_path = os.path.join(processed_dir, "Combined_Video.mp4")
            strain_strain_png = os.path.join(processed_dir, "Stress-Strain_Plot.png")
            compliance_png = os.path.join(processed_dir, "Compliance.png")
            pressure_diameter_png = os.path.join(processed_dir, "Pressure-Diameter.png")
            output_video = os.path.join(processed_dir, video_name)
            output_csv = os.path.join(processed_dir, csv_name)

            writer = cv2.VideoWriter(
                output_video,
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (width, height)
            )

            diameter_list = []
            frames = []
            frame_index = 0

            while self.running:
                ret, frame = vid.read()
                if not ret:
                    break

                frame_index += 1
                processed_frame, diameter = self.process_frame(frame)
                writer.write(processed_frame)
                frames.append(processed_frame)
                diameter_list.append(diameter if diameter is not None else 0)

            utils.log("Analysis Worker", "Video Processing Completed.")
            utils.log("Analysis Worker", "Processing Outputs. Please wait...")

            vid.release()
            writer.release()

            df["Diameter [px]"] = diameter_list[:len(df)]
            df["Diameter [px]"] = df["Diameter [px]"].round(2)

            pressure = df["Pressure [kPa]"]
            diameter = df["Diameter [px]"]

            # Reference (low pressure) state.
            P0 = pressure.iloc[0]
            D0 = diameter.iloc[0]

            # Calculate stress and strain.
            df["Stress [kPa]"] = pressure - P0
            df["Strain"] = (diameter - D0) / D0

            # rolling(window=5, min_periods=1, center=True).mean()
            df["Stress [kPa]"] = df["Stress [kPa]"].round(5)
            df["Strain"] = df["Strain"].round(5)

            processed_df = df[["Elapsed Time [s]", "Pressure [kPa]", "Diameter [px]", "Stress [kPa]", "Strain"]]
            processed_df.to_csv(output_csv, index=False)

            # Stress-Strain Graph.
            plt.figure(figsize=(8, 5))
            plt.plot(df["Strain"], df["Stress [kPa]"], color='red', linewidth=2)
            plt.xlabel(r"Circumferential Strain, $\epsilon_\theta$")
            plt.ylabel(r"Hoop Stress, $\sigma_\theta$ [kPa]")
            plt.title("Hoop Stress vs Circumferential Strain")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(strain_strain_png, dpi=300)
            plt.close()

            # Circumferential Compliance Graph.
            with np.errstate(divide='ignore', invalid='ignore'):
                compliance = df["Strain"] / df["Stress [kPa]"]
                compliance.replace([np.inf, -np.inf], np.nan, inplace=True)
            plt.figure(figsize=(8, 5))
            plt.plot(df["Elapsed Time [s]"], compliance, color='green', linewidth=2)
            plt.xlabel("Elapsed Time [s]")
            plt.ylabel(r"Circumferential Compliance, C$_\theta$ [1/kPa]")
            plt.title("Circumferential Compliance vs Time")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(compliance_png, dpi=300)
            plt.close()

            # Diameter and Pressure vs. Time Graph.
            fig, ax1 = plt.subplots(figsize=(8, 5))
            ax1.set_xlabel("Elapsed Time [s]")
            ax1.set_ylabel("Pressure [kPa]", color='orange')
            ax1.plot(df["Elapsed Time [s]"], df["Pressure [kPa]"], color='orange', linewidth=2, label="Pressure")
            ax1.tick_params(axis='y', labelcolor='orange')

            ax2 = ax1.twinx()
            ax2.set_ylabel("Diameter [px]", color='blue')
            ax2.plot(df["Elapsed Time [s]"], df["Diameter [px]"], color='blue', linewidth=2, label="Diameter")
            ax2.tick_params(axis='y', labelcolor='blue')

            plt.title("Pressure and Diameter vs Time")
            ax1.grid(True)
            fig.tight_layout()
            plt.savefig(pressure_diameter_png, dpi=300)
            plt.close()



            # Combined video w/ video & graph.
            combined_width, combined_height = 1280, 480
            graph_width, graph_height = 640, 480
            combined_writer = cv2.VideoWriter(
                combined_video_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (combined_width, combined_height)
            )

            # Precompute fixed axis limits.
            x_min, x_max = df["Strain"].min(), df["Strain"].max() * 1.1
            y_min, y_max = df["Stress [kPa]"].min(), df["Stress [kPa]"].max() * 1.1

            for i, frame in enumerate(frames):
                plt.figure(figsize=(6.4, 4.8), dpi=100)
                plt.plot(df["Strain"][:i+1], df["Stress [kPa]"][:i+1], color='blue', linewidth=2)
                plt.xlabel(r"Circumferential Strain, $\epsilon_\theta$")
                plt.ylabel(r"Hoop Stress, $\sigma_\theta$ [kPa]")
                plt.title("Stress vs Strain")
                plt.grid(True)
                plt.xlim(x_min, x_max)
                plt.ylim(y_min, y_max)

                # Render figure to numpy array
                from io import BytesIO
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=100)
                buf.seek(0)
                img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
                buf.close()
                graph_img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
                graph_img = cv2.cvtColor(graph_img, cv2.COLOR_RGB2BGR)
                graph_img = cv2.resize(graph_img, (graph_width, graph_height))
                plt.close()

                # Combine video frame and graph side by side
                combined_frame = np.hstack((frame, graph_img))
                combined_writer.write(combined_frame)

            combined_writer.release()

            utils.log("Analysis Worker", f"Processed CSV: {output_csv}.")
            utils.log("Analysis Worker", f"Processed Video: {output_video}.")
            utils.log("Analysis Worker", f"Combined Video: {combined_video_path}.")
            utils.log("Analysis Worker", f"Stress-Strain PNG: {strain_strain_png}.")
            utils.log("Analysis Worker", f"Compliance PNG: {compliance_png}.")
            utils.log("Analysis Worker", f"Pressure-Diameter PNG: {pressure_diameter_png}.")
            utils.log("Analysis Worker", "Analysis Completed.")

        except Exception as e:
            utils.log("Analysis Worker", f"Error: {e}.")


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
            cv2.line(debug, (col, top_limit), (col, bottom_limit), (0, 0, 0), 1)

            # Draw diameter.
            cv2.circle(debug, (col, top_y), 4, (0, 255, 0), -1)
            cv2.circle(debug, (col, bottom_y), 4, (0, 255, 0), -1)
            cv2.line(debug, (col, top_y), (col, bottom_y), (0, 0, 0), 2)

            cv2.putText(
                debug,
                f"{diameter}px",
                (col + 5, top_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
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

            # Averaging the diameters detected.
            if len(diameters) > 0:
                median = np.median(diameters)
                # replace values more than X px away from median with median
                capped = [d if abs(d - median) < 100 else median for d in diameters]
                avg_diameter = float(np.mean(capped))
            else:
                avg_diameter = None

        # Draw averaged diameter.
        cv2.putText(
            debug,
            f"Diameter: {avg_diameter:.2f}px",
            (420, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        return debug, avg_diameter
        
    def stop(self):
        self.running = False
