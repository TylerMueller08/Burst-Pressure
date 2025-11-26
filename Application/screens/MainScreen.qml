import QtQuick
import QtQuick.Controls
import "themes"

Item {
    visible: true
    signal goToMainScreen()
    signal goToRecordScreen()
    signal goToAnalysisScreen()

    Label {
        text: "Please select an option below to proceed:"
        anchors {
            top: parent.top
            topMargin: 250
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.headerSize
        }
    }

    Row {
        spacing: 40
        anchors {
            bottom: parent.bottom
            bottomMargin: 150
            horizontalCenter: parent.horizontalCenter
        }
        
        Button {
            id: recordButton
            width: 225; height: 70
            text: "Record"
            font {
                family: Theme.fontFamily
                pointSize: Theme.buttonSize
            }
            onClicked: { goToRecordScreen() }
            HoverHandler { cursorShape: Qt.PointingHandCursor }
        }

        Button {
            id: analysisButton
            width: 225; height: 70
            text: "Analysis"
            font {
                family: Theme.fontFamily
                pointSize: Theme.buttonSize
            }
            onClicked: { goToAnalysisScreen() }
            HoverHandler { cursorShape: Qt.PointingHandCursor }
        }
    }
}
