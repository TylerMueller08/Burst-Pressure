import sys, os
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from servicehandler import ServiceHandler
from analysishandler import AnalysisHandler

def main():
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_THEME"] = "Dark"

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    services = ServiceHandler()
    engine.rootContext().setContextProperty("Services", services)
    app.aboutToQuit.connect(services.disconnect)

    analysis = AnalysisHandler()
    engine.rootContext().setContextProperty("Analysis", analysis)

    engine.load("main.qml")
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
