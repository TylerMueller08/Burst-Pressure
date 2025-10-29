import cv2
import threading
import numpy as np
from collections import deque
import time

class VideoLogger:
    def __init__(self, camIndex=0, smoothWindow=5):
        self.camIndex = camIndex
        self.cam = cv2.VideoCapture(camIndex)
        self.frameWidth = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cam.get(cv2.CAP_PROP_FPS) or 30
        self.out = None

        self.latestDiameter = None
        self.lock = threading.Lock()
        self.diameter_history = deque(maxlen=smoothWindow)

        self.stop_event = threading.Event()
        self.thread = None

    def controlLoop(self):
        while not self.stop_event.is_set():
            ret, frame = self.cam.read()
            if not ret:
                time.sleep(0.01)
                continue
                
            debug_frame, diameter = self.process_frame(frame)

            cv2.imshow("Debug Diameter", debug_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_event.set()
                break
            
            with self.lock:
                self.latestDiameter = diameter

            if self.out:
                try:
                    self.out.write(frame)
                except Exception as e:
                    print(f"Video Write Error: {e}")
            
        try:
            if self.out:
                self.out.release()
        except Exception as e:
            print(f"Error Releasing VideoWriter: {e}")
        try:
            self.cam.release()
        except Exception as e:
            print(f"Error Releasing Camera: {e}")
        cv2.destroyAllWindows()

    def start(self, filename):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(filename, fourcc, self.fps, (self.frameWidth, self.frameHeight))
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.controlLoop, daemon=True)
        self.thread.start()

    def stop(self, join_timeout=2.0):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=join_timeout)
        if self.thread is None or not self.thread.is_alive():
            try:
                if self.out:
                    self.out.release()
            except Exception as e:
                print(f"Error releasing out in stop: {e}")
            try:
                self.cam.release()
            except Exception as e:
                print(f"Error releasing cam in stop: {e}")
            cv2.destroyAllWindows()
        else:
            print("Warning: VideoLogger thread did not stop within timeout.")

    def getLatestDiameter(self):
        with self.lock:
            return self.latestDiameter
        
    def process_frame(self, frame):
        border_ignore_frac = 0.12
        central_window_frac = 0.12

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
