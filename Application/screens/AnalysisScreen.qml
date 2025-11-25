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
        text: "Coming Soon"
        anchors {
            top: parent.top; topMargin: 200
            horizontalCenter: parent.horizontalCenter
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font {
            family: Theme.fontFamily
            pointSize: Theme.headerFontSize
        }
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
        id: startButton
        enabled: false
        text: "Test"
        width: 225; height: 70
        anchors {
            bottom: parent.bottom; bottomMargin: 50
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.buttonFontSize
            bold: true
        }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
    }
}