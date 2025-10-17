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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(gray, 50, 150)

        h, w = edges.shape
        mask = np.zeros_like(edges)
        mask[int(0.1*h):int(0.9*h), int(0.1*w):int(0.9*w)] = 255
        edges = cv2.bitwise_and(edges, mask)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        if len(contours) < 2:
            return frame, None

        contour_centers = []
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                contour_centers.append((cx, c))

        if len(contour_centers) < 2:
            return frame, None
            
        contour_centers = sorted(contour_centers, key=lambda k: k[0])
        leftContour = contour_centers[0][1]
        rightContour = contour_centers[-1][1]

        leftX = np.mean(leftContour[:, 0, 0]) # np.min
        rightX = np.mean(rightContour[:, 0, 0]) # np.max
        diameter = rightX - leftX

        self.diameter_history.append(diameter)
        smoothed_diameter = int(np.mean(self.diameter_history))

        cv2.drawContours(frame, [leftContour], -1, (0, 255, 0), 2)
        cv2.drawContours(frame, [rightContour], -1, (0, 255, 0), 2)
        cv2.putText(frame, f"Diameter: {smoothed_diameter:.1f}px", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return frame, smoothed_diameter
        