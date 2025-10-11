import cv2
import threading
import numpy as np

class VideoLogger:
    def __init__(self, camIndex=0):
        self.cam = cv2.VideoCapture(camIndex)
        self.frameWidth = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cam.get(cv2.CAP_PROP_FPS) or 30
        self.out = None
        self.recording = False
        self.latestDiameter = None
        self.lock = threading.Lock()

    def measureDiameter(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

        verticalSum = np.sum(thresh, axis=0)
        indices = np.where(verticalSum > 0)[0]
        if len(indices) > 1:
            return indices[-1] - indices[0] # Return width [pixels]
        return None
    
    def controlLoop(self):
        while self.recording:
            ret, frame = self.cam.read()
            if not ret:
                break
                
            diameter = self.measureDiameter(frame)
            with self.lock:
                self.latestDiameter = diameter

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

    def getLatestDiameter(self):
        with self.lock:
            return self.latestDiameter
