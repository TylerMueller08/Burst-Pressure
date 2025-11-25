import cv2, threading, utils

class VideoLogger:
    def __init__(self, pressure_handler=None, start_time=None):
        self.start_time = start_time
        self.pressure_handler = pressure_handler
        self.capture = None
        self.out = None
        self.thread = None
        self.running = False

    def start(self, prefix):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            utils.log("Video Logger", "No camera found")
            return
        
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.capture.get(cv2.CAP_PROP_FPS)) or 30

        utils.ensure_dir("data")
        filename = f"data/{prefix}_{utils.timestamp()}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        utils.log("Video Logger", f"Recording Started: {filename}")

        self.running = True
        self.thread = threading.Thread(target=self.record, daemon=True)
        self.thread.start()

    def record(self):
        while self.running and self.capture.isOpened():
            ret, frame = self.capture.read()
            if not ret:
                break

            elapsed_label = f"Time: {utils.elapsed(self.start_time):.1f}s"
            # pressure_label = f"Pressure: {self.pressure_handler.read():.2f}PSI"
            pressure_label = "N/A PSI"

            cv2.putText(frame, elapsed_label, (10, frame.shape[0]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, pressure_label, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            self.out.write(frame)
            cv2.imshow("Video Debug", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.running = False
                break
        self.cleanup()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def cleanup(self):
        if self.capture:
            self.capture.release()
        if self.out:
            self.out.release()
        cv2.destroyAllWindows()
        utils.log("Video Logger", "Recording Stopped")
