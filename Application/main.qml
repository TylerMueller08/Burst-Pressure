import QtQuick
import QtQuick.Controls
import "screens/themes"

Window {
    id: window
    visible: true
    width: 800
    height: 450
    title: "Burst Pressure Application"

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: "screens/MainScreen.qml"
        background: Rectangle { color: "#2B2B2B" }
    }

    Label {
        text: "Burst Pressure Application"
        anchors {
            top: parent.top; topMargin: 75
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
        text: "Adapted by Tyler Mueller (2025)"
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
        target: stackView.currentItem
        function onGoToMainScreen() { stackView.push("screens/MainScreen.qml") }
        function onGoToCaptureScreen() {
            stackView.push("screens/CaptureScreen.qml")
            services.reconnect()
            services.launchCamera()
        }
        function onGoToAnalysisScreen() { stackView.push("screens/AnalysisScreen.qml") }
    }
}
