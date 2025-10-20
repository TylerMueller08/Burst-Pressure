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
        border_ignore_frac = 0.12
        central_window_frac = 0.12
        min_valid_columns = 5

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        gray = cv2.GaussianBlur(gray, (9, 9), 0)

        x0 = int(w * border_ignore_frac)
        x1 = int(w * (1 - border_ignore_frac))
        y0 = int(h * border_ignore_frac)
        y1 = int(h * (1 - border_ignore_frac))
        roi = gray[y0:y1, x0:x1]

        cx = (x1 - x0) // 2
        half_win = int((central_window_frac * (x1 - x0)) / 2 )
        slice_roi = roi[:, cx-half_win:cx+half_win]
        profile = np.mean(slice_roi, axis=1)

        diff = np.diff(profile)

        top_rel = np.argmin(diff[:len(diff) // 2])
        bottom_rel = np.argmax(diff[len(diff) // 2:]) + len(diff) // 2

        top_y = top_rel + y0
        bottom_y = bottom_rel + y0
        cx_full = cx + x0

        diameter = None
        smoothed = None
        if bottom_y > top_y:
            diameter = float(bottom_y - top_y)
            self.diameter_history.append(diameter)
            smoothed = float(np.mean(self.diameter_history))

        debug = frame.copy()
        cv2.rectangle(debug, (x0, y0), (x1, y1), (60, 60, 60), 1)

        if smoothed is not None:
            cv2.line(debug, (cx_full, top_y), (cx_full, bottom_y), (0, 0, 255), 2)
            cv2.circle(debug, (cx_full, top_y), 4, (0, 255, 0), -1)
            cv2.circle(debug, (cx_full, bottom_y), 4, (0, 255, 0), -1)
            cv2.putText(debug, f"Diameter: {smoothed:.1f}px", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        else:
            cv2.putText(debug, "Diameter: N/A", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        return debug, smoothed
