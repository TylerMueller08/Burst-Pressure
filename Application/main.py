import sys, os
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from servicehandler import ServiceHandler

def main():
    os.environ["QT_QUICK_CONTROLS_CONF"] = os.path.join(os.path.dirname(__file__), "themes/qtquickcontrols2.conf")

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    services = ServiceHandler()
    engine.rootContext().setContextProperty("services", services)
    app.aboutToQuit.connect(services.disconnect)

    engine.load("main.qml")
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
