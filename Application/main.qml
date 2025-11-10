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
            id: pressureConnection
            text: "Pressure " + services.pressure_connected()
            height: 24
            anchors {
                top: parent.top; topMargin: 130
                horizontalCenter: parent.horizontalCenter
            }
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font {
                family: Theme.fontFamily
                pointSize: Theme.textFontSize
            }
        }

        Label {
            id: relayConnection
            text: "Relay " + services.relay_connected()
            height: 24
            anchors {
                top: parent.top; topMargin: 170
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
            text: checked ? "Stop" : "Start"
            width: 160; height: 80
            checkable: true
            anchors {
                top: parent.top; topMargin: 225
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

        Button {
            text: "Refresh"
            width: 110; height: 50
            anchors {
                left: parent.left; leftMargin: 6
                bottom: parent.bottom; bottomMargin: 6
            }
            font {
                family: Theme.fontFamily
                pointSize: Theme.watermarkFontSize
                bold: true
            }
            onClicked: {
                services.reload()
                pressureConnection.text = "Pressure " + services.pressure_connected()
                relayConnection.text = "Relay " + services.relay_connected()
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
