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
                
            debug_frame = self.process_frame(frame)
            cv2.imshow("Debug Diameter", debug_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
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
        
    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7,7), 0)

        # Threshold for bright object vs background
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

        # Morphological closing to remove text holes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,15))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)

            rect = cv2.minAreaRect(c)  
            box = cv2.boxPoints(rect).astype(int)

            cv2.drawContours(frame, [box], 0, (0,255,0), 2)

            width, height = rect[1]
            diameter = min(width, height)

            center = tuple(map(int, rect[0]))
            cv2.putText(frame, f"Diameter: {int(diameter)}px", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return frame