import cv2
import threading
import numpy as np
from collections import deque

class VideoLogger:
    def __init__(self, camIndex=0, smoothWindow=5):
        self.cam = cv2.VideoCapture(camIndex)
        self.frameWidth = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cam.get(cv2.CAP_PROP_FPS) or 30
        self.out = None
        self.recording = False
        self.latestDiameter = None
        self.lock = threading.Lock()
        self.diameter_history = deque(maxlen=smoothWindow)

    def measureDiameter(self, frame):
        _, diameter = self.process_frame(frame)
        return diameter

    def controlLoop(self):
        while self.recording:
            ret, frame = self.cam.read()
            if not ret:
                break
                
            debug_frame, diameter = self.process_frame(frame)

            cv2.imshow("Debug Diameter", debug_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # diameter = self.measureDiameter(frame)
            with self.lock:
                self.latestDiameter = diameter

            if self.out:
                self.out.write(frame)

    def start(self, filename):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(filename, fourcc, self.fps, (self.frameWidth, self.frameHeight))
        self.recording = True
        threading.Thread(target=self.controlLoop, daemon=True).start()

    def stop(self):
        self.recording = False
        if self.out:
            self.out.release()
        self.cam.release()
        cv2.destroyAllWindows()

    def getLatestDiameter(self):
        with self.lock:
            return self.latestDiameter
        
    def process_frame(self, frame):
        # Parameters you can tune
        border_ignore_frac = 0.04   # fraction of width/height to ignore around edges
        central_window_frac = 0.12  # fraction of width used around center to average
        min_valid_columns = 5       # require at least this many columns in central window
        low_canny = 30
        high_canny = 100

        h, w = frame.shape[:2]

        # 1) Preprocess image for stable edges
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Improve local contrast (CLAHE) to handle uneven lighting
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # Slight blur to reduce small speckle noise
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # 2) Mask out the outer border area which often contains the strong rectangle edge
        x0 = int(w * border_ignore_frac)
        x1 = int(w * (1 - border_ignore_frac))
        y0 = int(h * border_ignore_frac)
        y1 = int(h * (1 - border_ignore_frac))
        mask = np.zeros_like(gray, dtype=np.uint8)
        mask[y0:y1, x0:x1] = 255
        # apply mask to gray before edge detection
        masked = cv2.bitwise_and(gray, gray, mask=mask)

        # 3) Morphological close to join broken tube edges (helps for some noisy frames)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 3))
        morph = cv2.morphologyEx(masked, cv2.MORPH_CLOSE, kernel)

        # 4) Canny
        edges = cv2.Canny(morph, low_canny, high_canny)

        # Optional: remove small isolated edge blobs
        # find connected components and remove small areas
        nb_components, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
        cleaned = np.zeros_like(edges)
        min_area = 30
        for i in range(1, nb_components):
            if stats[i, cv2.CC_STAT_AREA] >= min_area:
                cleaned[labels == i] = 255
        edges = cleaned

        # 5) Column-wise scan: for each x, find topmost and bottommost edge pixel
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

        # 6) Focus on a central vertical slice for the diameter measurement
        cx = w // 2
        half_win = int((central_window_frac * w) / 2)
        cx0 = max(left, cx - half_win)
        cx1 = min(right - 1, cx + half_win)

        valid_tops = []
        valid_bottoms = []
        for x in range(cx0, cx1 + 1):
            if x in tops and x in bottoms and bottoms[x] > tops[x]:
                valid_tops.append(tops[x])
                valid_bottoms.append(bottoms[x])

        diameter = None
        if len(valid_tops) >= min_valid_columns:
            # Compute robust stats (median) across the central columns
            top_m = int(np.median(valid_tops))
            bot_m = int(np.median(valid_bottoms))
            diameter = float(bot_m - top_m)

            # smoothing history
            self.diameter_history.append(diameter)
            smoothed = float(np.mean(self.diameter_history))
        else:
            # fallback: try taking median across all detected columns (if central failed)
            all_tops = list(tops.values())
            all_bottoms = list(bottoms.values())
            if len(all_tops) >= min_valid_columns:
                top_m = int(np.median(all_tops))
                bot_m = int(np.median(all_bottoms))
                diameter = float(bot_m - top_m)
                self.diameter_history.append(diameter)
                smoothed = float(np.mean(self.diameter_history))
            else:
                # no reliable detection
                smoothed = None

        # 7) Visualization overlay for debugging
        debug = frame.copy()

        # draw the masked ROI rectangle
        cv2.rectangle(debug, (x0, y0), (x1, y1), (60, 60, 60), 1)

        # draw top/bottom edge points in central region
        for x in range(cx0, cx1 + 1):
            if x in tops:
                debug = cv2.circle(debug, (x, tops[x]), 1, (0, 255, 0), -1)
            if x in bottoms:
                debug = cv2.circle(debug, (x, bottoms[x]), 1, (0, 255, 0), -1)

        if smoothed is not None:
            # draw the center vertical line at cx with length smoothed
            # compute the top/bottom Y at center by averaging a tiny window
            # use previously computed top_m/bot_m if available
            if 'top_m' not in locals():
                top_m = int(np.median(valid_tops)) if valid_tops else int(np.median(all_tops))
                bot_m = int(np.median(valid_bottoms)) if valid_bottoms else int(np.median(all_bottoms))
            # draw the red vertical diameter line at center x
            cv2.line(debug, (cx, top_m), (cx, bot_m), (0, 0, 255), 2)

            # annotation
            cv2.putText(debug, f"Diameter: {smoothed:.1f}px", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        else:
            cv2.putText(debug, "Diameter: N/A", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        return debug, smoothed
        