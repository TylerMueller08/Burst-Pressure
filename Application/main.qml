import QtQuick
import QtQuick.Controls
import "themes"

ApplicationWindow {
    id: window
    visible: true
    width: 600
    height: 360
    title: "Burst Pressure Manager"

    Component.onCompleted: {
        services.reconnect()
        services.launchCamera()
    }

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
            id: pressureIndicator
            text: "Pressure: N/A"
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
            id: relayIndicator
            text: "Relay: N/A"
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

        TextField {
            id: nameField
            placeholderText: "Identifier"
            width: 225; height: 35
            anchors {
                bottom: parent.bottom; bottomMargin: 125
                horizontalCenter: parent.horizontalCenter
            }
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font {
                family: Theme.fontFamily
                pointSize: Theme.inputFontSize
            }
            selectionColor: "#FFFFFF"
            cursorVisible: true
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
            id: startButton
            text: checked ? "Stop" : "Start"
            width: 165; height: 60
            checkable: true
            anchors {
                bottom: parent.bottom; bottomMargin: 50
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

    Connections {
        target: services
        function onPressureUpdated(connected) {
            pressureIndicator.text = "Pressure: " + (connected ? "Connected" : "Disconnected")
        }

        function onRelayUpdated(connected) {
            relayIndicator.text = "Relay: " + (connected ? "Connected" : "Disconnected")
        }

        function onConnected(connected) {
            startButton.enabled = connected
        }
    }
}
