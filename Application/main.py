import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from servicehandler import ServiceHandler

def main():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    services = ServiceHandler()
    engine.rootContext().setContextProperty("services", services)

    engine.load("main.qml")
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
