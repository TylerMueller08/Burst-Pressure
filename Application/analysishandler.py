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
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(None, "Select Folder Containing Video and CSV")
        if not folder:
            return

        import os
        csv_path = None
        video_path = None

        for file in os.listdir(folder):
            lower = file.lower()
            if lower.endswith(".csv"):
                csv_path = os.path.join(folder, file)
            elif lower.endswith(".mp4"):
                video_path = os.path.join(folder, file)

        if csv_path:
            utils.log("Analysis Handler", f"Successfully selected CSV: {csv_path}")
            self.csvUpdated.emit(csv_path)
        else:
            utils.log("Analysis Handler", "Failed to find a CSV file in the selected folder.")

        if video_path:
            utils.log("Analysis Handler", f"Successfully selected Video: {video_path}")
            self.videoUpdated.emit(video_path)
        else:
            utils.log("Analysis Handler", "Failed to find a Video file in the selected folder.")
