import QtQuick
import QtQuick.Controls
import "themes"

Item {
    visible: true
    signal goToMainScreen()
    signal goToRecordScreen()
    signal goToAnalysisScreen()

    Label {
        text: "Coming Soon"
        anchors {
            top: parent.top
            topMargin: 200
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.headerSize
        }
    }

    Button {
        id: startButton
        width: 225; height: 75
        text: "Test"
        enabled: false
        anchors {
            bottom: parent.bottom
            bottomMargin: 50
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.buttonSize
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
}