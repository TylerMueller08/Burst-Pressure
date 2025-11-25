import base64
import csv
import io
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, Property, QMutex, QMutexLocker
from PySide6.QtWidgets import QFileDialog

def encode_frame_to_data_url(frame):
    # frame is BGR numpy array
    ret, buf = cv2.imencode('.png', frame)
    if not ret:
        return ""
    b64 = base64.b64encode(buf).decode('ascii')
    return f"data:image/png;base64,{b64}"

class VideoAnalyzer(QObject):
    # Signals
    progressChanged = Signal(int) # percent
    frameReady = Signal(str) # data-url string for QML Image
    analysisFinished = Signal()
    logMessage = Signal(str)
    csvExported = Signal(str) # path
    videoExported = Signal(str) # path

    def __init__(self, parent=None):
        super().__init__(parent)
        self._video_path = ""
        self._cap = None
        self._fps = 30.0
        self._frame_count = 0
        self._width = 0
        self._height = 0

        # default params (tunable from QML)
        self.low_canny = 30
        self.high_canny = 100
        self.clahe_clip = 2.0
        self.blur_ksize = 5 # odd
        self.morph_kernel_w = 7
        self.morph_kernel_h = 3
        self.border_ignore_frac = 0.04
        self.central_window_frac = 0.12
        self.min_valid_columns = 5
        self.smooth_window = 5
        self.sample_frame_step = 1 # analyze every frame by default (increase to speed up)
        self._running = False
        self._mutex = QMutex()
        self._latest_frame_dataurl = ""
        self._diameter_history = []
        self._pressure_times = None
        self._pressure_values = None

    @Slot(result=str)
    def openFileDialog(self):
        """Open a native file dialog starting in './data' and return selected path (or '')"""
        start_dir = str(Path.cwd() / "data")
        path, _ = QFileDialog.getOpenFileName(None, "Open Video", start_dir, "Video Files (*.mp4 *.avi *.mov)")
        if path:
            self.load_video(path)
        return path or ""

    @Slot(str)
    def load_video(self, path):
        """Open video and set metadata"""
        if not Path(path).exists():
            self.logMessage.emit(f"Video not found: {path}")
            return
        self._video_path = path
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            self.logMessage.emit("Failed to open video.")
            return
        self._cap = cap
        self._frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._fps = fps if fps > 0 else 30.0
        self._width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        self._height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        self._diameter_history = []
        self.logMessage.emit(f"Loaded video {path} - {self._frame_count} frames, {self._fps:.2f} fps, {self._width}x{self._height}")
        # show first frame in UI
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self._cap.read()
        if ret:
            url = encode_frame_to_data_url(frame)
            with QMutexLocker(self._mutex):
                self._latest_frame_dataurl = url
            self.frameReady.emit(url)

    @Slot(int)
    def preview_frame(self, frame_index):
        """Compute detection on a single frame and emit data-url for display (so user can tune params)"""
        if not self._cap:
            return
        fi = max(0, min(self._frame_count - 1, frame_index))
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ret, frame = self._cap.read()
        if not ret:
            return
        debug, diameter = self._process_frame(frame)
        url = encode_frame_to_data_url(debug)
        with QMutexLocker(self._mutex):
            self._latest_frame_dataurl = url
        self.frameReady.emit(url)
        self.logMessage.emit(f"Preview frame {fi}, measured diameter = {diameter}")

    def _process_frame(self, frame):
        """Return (debug_frame_BGR, diameter_px or None) - copied/adapted from your old code"""
        # Ensure grayscale
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=self.clahe_clip, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # blur
        k = self.blur_ksize if self.blur_ksize % 2 == 1 else self.blur_ksize + 1
        gray = cv2.GaussianBlur(gray, (k, k), 0)

        # ROI mask (ignore borders to avoid camera housing edges)
        x0 = int(w * self.border_ignore_frac)
        x1 = int(w * (1 - self.border_ignore_frac))
        y0 = int(h * self.border_ignore_frac)
        y1 = int(h * (1 - self.border_ignore_frac))
        mask = np.zeros_like(gray, dtype=np.uint8)
        mask[y0:y1, x0:x1] = 255
        masked = cv2.bitwise_and(gray, gray, mask=mask)

        # Morph close to join edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.morph_kernel_w, self.morph_kernel_h))
        morph = cv2.morphologyEx(masked, cv2.MORPH_CLOSE, kernel)

        # Canny
        edges = cv2.Canny(morph, self.low_canny, self.high_canny)

        # remove tiny components
        nb_components, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
        cleaned = np.zeros_like(edges)
        min_area = 30
        for i in range(1, nb_components):
            if stats[i, cv2.CC_STAT_AREA] >= min_area:
                cleaned[labels == i] = 255
        edges = cleaned

        # column-wise scan
        left = x0
        right = x1
        tops = {}
        bottoms = {}
        for x in range(left, right):
            col = edges[:, x]
            ys = np.nonzero(col)[0]
            if ys.size:
                tops[x] = int(ys[0])
                bottoms[x] = int(ys[-1])

        # central slice analysis
        cx = w // 2
        half_win = int((self.central_window_frac * w) / 2)
        cx0 = max(left, cx - half_win)
        cx1 = min(right - 1, cx + half_win)

        valid_tops = []
        valid_bottoms = []
        for x in range(cx0, cx1 + 1):
            if x in tops and x in bottoms and bottoms[x] > tops[x]:
                valid_tops.append(tops[x])
                valid_bottoms.append(bottoms[x])

        diameter = None
        if len(valid_tops) >= self.min_valid_columns:
            top_m = int(np.median(valid_tops))
            bot_m = int(np.median(valid_bottoms))
            diameter = float(bot_m - top_m)
            self._diameter_history.append(diameter)
            smoothed = float(np.mean(self._diameter_history[-self.smooth_window:]))
        else:
            # fallback to global median
            all_tops = list(tops.values())
            all_bottoms = list(bottoms.values())
            if len(all_tops) >= self.min_valid_columns:
                top_m = int(np.median(all_tops))
                bot_m = int(np.median(all_bottoms))
                diameter = float(bot_m - top_m)
                self._diameter_history.append(diameter)
                smoothed = float(np.mean(self._diameter_history[-self.smooth_window:]))
            else:
                smoothed = None

        # visualization
        debug = frame.copy()
        cv2.rectangle(debug, (x0, y0), (x1, y1), (60, 60, 60), 1)
        for x in range(cx0, cx1 + 1):
            if x in tops:
                cv2.circle(debug, (x, tops[x]), 1, (0, 255, 0), -1)
            if x in bottoms:
                cv2.circle(debug, (x, bottoms[x]), 1, (0, 255, 0), -1)

        if smoothed is not None:
            # draw center vertical line at cx using top_m/bot_m if available
            try:
                # top_m and bot_m often exist above
                cv2.line(debug, (cx, top_m), (cx, bot_m), (0, 0, 255), 2)
                cv2.putText(debug, f"Diameter: {smoothed:.1f}px", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            except Exception:
                cv2.putText(debug, f"Diameter: {smoothed:.1f}px", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        else:
            cv2.putText(debug, "Diameter: N/A", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        return debug, smoothed

    @Slot()
    def cancel(self):
        with QMutexLocker(self._mutex):
            self._running = False

    @Slot()
    def run_analysis(self):
        if not self._cap or not self._video_path:
            self.logMessage.emit("No video loaded")
            return
        # ensure not already running
        with QMutexLocker(self._mutex):
            if self._running:
                self.logMessage.emit("Already running")
                return
            self._running = True

        t = threading.Thread(target=self._analysis_loop, daemon=True)
        t.start()

    def _analysis_loop(self):
        """Walk through video frames, compute widths, collect timestamps and (optionally) pressure"""
        cap = cv2.VideoCapture(self._video_path)
        fps = self._fps
        total = self._frame_count
        out_records = []  # list of (elapsed_s, width_px)
        diam_history = []
        frame_idx = 0
        progress_emit = 0

        # For annotated video creation, we'll write frames to temp if user asks later. For preview emit frames occasionally.
        while True:
            with QMutexLocker(self._mutex):
                if not self._running:
                    self.logMessage.emit("Analysis canceled")
                    break

            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.sample_frame_step == 0:
                debug, diameter = self._process_frame(frame)
            else:
                diameter = None
                debug = frame

            elapsed = frame_idx / fps
            out_records.append((elapsed, float(diameter) if diameter is not None else float("nan")))

            # emit occasional frame for UI preview (every ~1s)
            if fps > 0 and (frame_idx % int(fps) == 0):
                url = encode_frame_to_data_url(debug)
                with QMutexLocker(self._mutex):
                    self._latest_frame_dataurl = url
                self.frameReady.emit(url)

            # progress
            if total > 0:
                new_progress = int((frame_idx / total) * 100)
                if new_progress != progress_emit:
                    progress_emit = new_progress
                    self.progressChanged.emit(progress_emit)
            frame_idx += 1

        cap.release()
        with QMutexLocker(self._mutex):
            self._running = False

        # store results
        self._analysis_results = out_records
        self.progressChanged.emit(100)
        self.logMessage.emit("Analysis complete")
        self.analysisFinished.emit()

    @Slot(str)
    def load_pressure_csv(self, path):
        """Load a DataLogger CSV produced by your DataLogger and store times & values for interpolation"""
        if not Path(path).exists():
            self.logMessage.emit("Pressure CSV not found")
            return
        times = []
        vals = []
        with open(path, newline='') as f:
            r = csv.reader(f)
            header = next(r, None)
            for row in r:
                if not row: continue
                try:
                    t = float(row[0])
                    p = float(row[1])
                except Exception:
                    # handle header-like rows
                    continue
                times.append(t)
                vals.append(p)
        if len(times) < 2:
            self.logMessage.emit("Pressure CSV has too few samples")
            return
        self._pressure_times = np.array(times)
        self._pressure_values = np.array(vals)
        self.logMessage.emit(f"Loaded pressure CSV ({len(times)} samples)")

    @Slot(str, result=str)
    def export_csv(self, out_path):
        """Export CSV with columns: 'Elapsed Time [s]', 'Pressure [PSI]', 'Tube Width [px]'.
           If pressure CSV loaded, pressure is interpolated. Otherwise Pressure column will be empty/NaN."""
        if not hasattr(self, "_analysis_results"):
            self.logMessage.emit("No analysis results to export")
            return ""
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["Elapsed Time [s]", "Pressure [PSI]", "Tube Width [px]"])
            for elapsed, width in self._analysis_results:
                if self._pressure_times is not None:
                    # interpolate
                    p = np.interp(elapsed, self._pressure_times, self._pressure_values, left=np.nan, right=np.nan)
                else:
                    p = float("nan")
                w.writerow([f"{elapsed:.3f}", f"{p:.3f}" if not np.isnan(p) else "", f"{width:.3f}" if not np.isnan(width) else ""])
        self.csvExported.emit(out_path)
        self.logMessage.emit(f"CSV exported: {out_path}")
        return out_path

    @Slot(str, result=str)
    def export_annotated_video(self, out_path):
        """Write a new mp4 annotated with diameter text/line on each frame. Uses the analysis results."""
        if not hasattr(self, "_analysis_results"):
            self.logMessage.emit("No analysis to export")
            return ""
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        cap = cv2.VideoCapture(self._video_path)
        if not cap.isOpened():
            self.logMessage.emit("Failed to open video for writing annotated")
            return ""
        fps = self._fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
        idx = 0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        for elapsed, width_val in self._analysis_results:
            ret, frame = cap.read()
            if not ret:
                break
            # overlay width text
            txt = f"Time: {elapsed:.3f}s  Width: {width_val:.2f}px"
            cv2.putText(frame, txt, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            out.write(frame)
            idx += 1
            if total > 0:
                self.progressChanged.emit(int((idx / total) * 100))
        cap.release()
        out.release()
        self.videoExported.emit(out_path)
        self.logMessage.emit(f"Annotated video exported: {out_path}")
        return out_path

    # small property to let QML read the last frame as a URL
    @Property(str, notify=frameReady)
    def frameData(self):
        with QMutexLocker(self._mutex):
            return self._latest_frame_dataurl or ""
