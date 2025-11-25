import QtQuick
import QtQuick.Controls
import "themes"

Item {
    id: mainScreen
    visible: true

    signal goToMainScreen()
    signal goToCaptureScreen()
    signal goToAnalysisScreen()

    Label {
        text: "Please select an option below to proceed:"
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

    Row {
        anchors {
            bottom: parent.bottom; bottomMargin: 125
            horizontalCenter: parent.horizontalCenter
        }
        spacing: 40
        
        Button {
            id: captureButton
            text: "Capture"
            width: 225; height: 70
            font {
                family: Theme.fontFamily
                pointSize: Theme.buttonFontSize
            }
            onClicked: {
                goToCaptureScreen()
            }
            HoverHandler { cursorShape: Qt.PointingHandCursor }
        }

        Button {
            id: analysisButton
            text: "Analysis"
            width: 225; height: 70
            font {
                family: Theme.fontFamily
                pointSize: Theme.buttonFontSize
            }
            onClicked: {
                goToAnalysisScreen()
            }
            HoverHandler { cursorShape: Qt.PointingHandCursor }
        }
    }
}
