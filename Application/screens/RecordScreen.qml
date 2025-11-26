import QtQuick
import QtQuick.Controls
import "themes"

Item {
    visible: true
    signal goToMainScreen()
    signal goToRecordScreen()
    signal goToAnalysisScreen()

    Label {
        id: relayIndicator
        text: "Relay: N/A"
        color: Theme.altTextColor
        anchors {
            top: parent.top
            topMargin: 180
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.headerSize
        }
    }
    
    Label {
        id: pressureIndicator
        text: "Pressure: N/A"
        color: Theme.altTextColor
        anchors {
            top: parent.top
            topMargin: 210
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.headerSize
        }
    }

    TextField {
        id: nameField
        width: 300; height: 55
        text: "Unlabeled"
        placeholderText: "Prefix"
        anchors {
            bottom: parent.bottom
            bottomMargin: 190
            horizontalCenter: parent.horizontalCenter
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font {
            family: Theme.fontFamily
            pointSize: Theme.inputSize
        }
    }

    Button {
        id: startButton
        text: checked ? "Stop" : "Start"
        width: 225; height: 70
        checkable: true
        anchors {
            bottom: parent.bottom
            bottomMargin: 75
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.buttonSize
        }
        onCheckedChanged: {
            if (checked) {
                Services.start(nameField.text)
            } else {
                Services.stop()
            }
        }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
    }

    Button {
        width: 80; height: 90
        anchors {
            left: parent.left
            leftMargin: 8
            bottom: parent.bottom
            bottomMargin: 4
        }
        icon {
            source: "themes/images/back.png"
            height: 40; width: 40
        }
        onClicked: { goToMainScreen() }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
    }

    Connections {
        target: Services
        function onPressureUpdated(connected) { pressureIndicator.text = "Pressure: " + (connected ? "Connected" : "Disconnected") }
        function onRelayUpdated(connected) { relayIndicator.text = "Relay: " + (connected ? "Connected" : "Disconnected") }
        function onConnected(connected) { startButton.enabled = connected }
    }
}
