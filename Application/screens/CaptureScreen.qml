import QtQuick
import QtQuick.Controls
import "themes"

Item {
    id: captureScreen
    visible: true

    signal goToMainScreen()
    signal goToCaptureScreen()
    signal goToAnalysisScreen()
    
    Label {
        id: pressureIndicator
        text: "Pressure: N/A"
        anchors {
            top: parent.top; topMargin: 160
            horizontalCenter: parent.horizontalCenter
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font {
            family: Theme.fontFamily
            pointSize: Theme.headerFontSize
        }
    }

    Label {
        id: relayIndicator
        text: "Relay: N/A"
        anchors {
            top: parent.top; topMargin: 190
            horizontalCenter: parent.horizontalCenter
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font {
            family: Theme.fontFamily
            pointSize: Theme.headerFontSize
        }
    }

    TextField {
        id: nameField
        placeholderText: "Prefix"
        width: 250; height: 50
        text: "Unlabeled"
        anchors {
            bottom: parent.bottom; bottomMargin: 140
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
        width: 80; height: 90
        anchors {
            left: parent.left; leftMargin: 8
            bottom: parent.bottom; bottomMargin: 4
        }
        icon.source: "themes/images/back.png"
        icon.height: 40; icon.width: 40
        onClicked: {
            goToMainScreen()
        }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
    }

    Button {
        width: 80; height: 90
        anchors {
            right: parent.right; rightMargin: 8
            bottom: parent.bottom; bottomMargin: 4
        }
        icon.source: "themes/images/refresh.png"
        icon.height: 36; icon.width: 36
        onClicked: {
            services.reconnect()
        }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
    }

    Button {
        id: startButton
        text: checked ? "Stop" : "Start"
        width: 225; height: 70
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
                services.start(nameField.text)
            } else {
                services.stop()
            }
        }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
    }

    Connections {
        target: services
        function onPressureUpdated(connected) { pressureIndicator.text = "Pressure: " + (connected ? "Connected" : "Disconnected") }
        function onRelayUpdated(connected) { relayIndicator.text = "Relay: " + (connected ? "Connected" : "Disconnected") }
        function onConnected(connected) { startButton.enabled = connected }
    }
}
