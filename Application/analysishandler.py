from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QFileDialog
from analysisworker import AnalysisWorker
import utils

class AnalysisHandler(QObject):
    csvUpdated = Signal(str)
    videoUpdated = Signal(str)

    def __init__(self):
        super().__init__()
        self.worker = None

    @Slot(str, str)
    def run_analysis(self, csv_path, video_path):
        if self.worker and self.worker.isRunning():
            utils.log("Analysis Handler", "Analysis Worker is already running")
            return
        
        self.worker = AnalysisWorker(csv_path, video_path)
        self.worker.start()

    @Slot()
    def select_csv(self):
        file, _ = QFileDialog.getOpenFileName(None, "Select CSV", "", "CSV Files (*.csv)")
        if file:
            utils.log("Analysis Handler", f"Successfully selected CSV: {file}")
            self.csvUpdated.emit(file)

    @Slot()
    def select_video(self):
        file, _ = QFileDialog.getOpenFileName(None, "Select Video", "", "Video Files (*.mp4)")
        if file:
            utils.log("Analysis Handler", f"Successfully selected video: {file}")
            self.videoUpdated.emit(file)

