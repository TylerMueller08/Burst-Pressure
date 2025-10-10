import cv2
import threading
from utils import currentTimestamp

class VideoLogger:
    def __init__(self, cam_index=0):
        self.cam = cv2.VideoCapture(cam_index)
        self.frame_width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cam.get(cv2.CAP_PROP_FPS) or 30
        self.out = None
        self.recording = False
    
    def _loop(self):
        while self.recording:
            ret, frame = self.cam.read()
            if not ret:
                print("Error: Could not read the camera frame.")
                break

            cv2.putText(frame, currentTimestamp, (10, self.frame_height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            self.out.write(frame)
        cv2.destroyAllWindows()

    def start(self, filename):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(filename, fourcc, self.fps, (self.frame_width, self.frame_height))
        self.recording = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.recording = False
        if self.out:
            self.out.release()
        self.cam.release()