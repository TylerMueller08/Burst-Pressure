import QtQuick
import QtQuick.Controls
import "themes"

ApplicationWindow {
    visible: true
    width: 600
    height: 360
    title: "Burst Pressure Manager"

    Rectangle {
        anchors.fill: parent
        color: "#2b2b2b"

        Label {
            text: "Burst Pressure Manager"
            height: 60
            anchors {
                top: parent.top; topMargin: 60
                horizontalCenter: parent.horizontalCenter
            }
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font {
                family: Theme.fontFamily
                pointSize: Theme.titleFontSize
                bold: true
            }
        }

        Label {
            id: connectionIndicator
            text: (services.pressure_connected() ? "Pressure: Connected" : "Pressure: Disconnected") + "\n" + (services.relay_connected() ? "Relay: Connected" : "Relay: Disconnected")
            anchors {
                top: parent.top; topMargin: 150
                horizontalCenter: parent.horizontalCenter
            }
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font {
                family: Theme.fontFamily
                pointSize: Theme.textFontSize
            }
        }

        Button {
            width: 65; height: 75
            anchors {
                left: parent.left; leftMargin: 8
                bottom: parent.bottom; bottomMargin: 5
            }
            
            icon.source: "themes/images/refresh.png"
            icon.height: 30; icon.width: 30

            onClicked: {
                services.reconnect()
            }
        }

        Button {
            text: checked ? "Stop" : "Start"
            width: 160; height: 70
            checkable: true
            enabled: services.pressure_connected() && services.relay_connected()
            anchors {
                bottom: parent.bottom; bottomMargin: 60
                horizontalCenter: parent.horizontalCenter
            }
            font {
                family: Theme.fontFamily
                pointSize: Theme.buttonFontSize
                bold: true
            }
            onCheckedChanged: {
                if (checked) {
                    services.start()
                } else {
                    services.stop()
                }
            }
        }
    }

    Label {
        text: "Revised by Tyler Mueller (2025)"
        anchors {
            bottom: parent.bottom; bottomMargin: 8
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.watermarkFontSize
        }
        opacity: 0.6
    }
}
