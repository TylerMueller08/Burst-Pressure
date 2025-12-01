import QtQuick
import QtQuick.Controls
import QtMultimedia
import "themes"

Item {
    id: analysisScreen
    visible: true

    signal goToMainScreen()
    signal goToRecordScreen()
    signal goToAnalysisScreen()

    property string csvFilePath: ""
    property string videoFilePath: ""

    Row {
        spacing: 20
        anchors {
            horizontalCenter: parent.horizontalCenter
            verticalCenter: parent.verticalCenter
        }
        Button {
            id: videoButton
            width: 250; height: 70
            text: videoFilePath === "" ? "Upload Video" : "Video Selected"
            font {
                family: Theme.fontFamily
                pointSize: Theme.inputSize
            }
            onClicked: Analysis.select_video()
            HoverHandler { cursorShape: Qt.PointingHandCursor }
        }
        Button {
            id: csvButton
            width: 250; height: 70
            text: csvFilePath === "" ? "Upload CSV" : "CSV Selected"
            font {
                family: Theme.fontFamily
                pointSize: Theme.inputSize
            }
            onClicked: Analysis.select_csv()
            HoverHandler { cursorShape: Qt.PointingHandCursor }
        }
    }

    Button {
        id: runButton
        width: 225; height: 75
        text: "Run"
        enabled: csvFilePath !== "" && videoFilePath !== ""
        anchors {
            bottom: parent.bottom
            bottomMargin: 50
            horizontalCenter: parent.horizontalCenter
        }
        font {
            family: Theme.fontFamily
            pointSize: Theme.buttonSize
        }
        onClicked: Analysis.run_analysis(csvFilePath, videoFilePath)
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
        target: Analysis
        function onVideoUpdated(file) {
            videoButton.enabled = false
            videoFilePath = file
        }
        function onCsvUpdated(file) {
            csvButton.enabled = false
            csvFilePath = file
        }
    }
}