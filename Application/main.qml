import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 480
    height: 360
    title: "Burst Pressure Manager"

    Rectangle {
        anchors.fill: parent
        color: "#2b2b2b"

        Text {
            text: "Text"
        }

        Button {
            text: checked ? "True" : "False"
            checkable: true

            onCheckedChanged: {
                if (checked) {
                    services.start()
                } else {
                    services.stop()
                }
            }
        }
    }
}
