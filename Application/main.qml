import QtQuick
import QtQuick.Controls
import "screens/themes"

Window {
    visible: true
    width: 960; height: 540
    title: "Burst Pressure Application"

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: "screens/MainScreen.qml"
        background: Rectangle { color: Theme.backgroundColor }
    }

    Label {
        text: "Burst Pressure Application"
        anchors.top: parent.top
        anchors.topMargin: 75
        anchors.horizontalCenter: parent.horizontalCenter
        font.family: Theme.fontFamily
	    font.pointSize: Theme.titleSize
	    font.bold: true
    }

    Label {
        text: "Adapted by Tyler Mueller (2025)"
        anchors {
            bottom: parent.bottom
            bottomMargin: 8
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.watermarkSize
        }
        opacity: 0.6
    }

    Connections {
        target: stackView.currentItem
        function onGoToMainScreen() {
            stackView.push("screens/MainScreen.qml")
            Services.disconnect()
        }
        function onGoToRecordScreen() {
            stackView.push("screens/RecordScreen.qml")
            Services.connect()
            Services.launch_camera()
        }
        function onGoToAnalysisScreen() { stackView.push("screens/AnalysisScreen.qml") }
    }
}
