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
    property bool filesReady: csvFilePath === "" && videoFilePath === ""

    Button {
        id: folderButton
	width: 250; height: 70
	text: filesReady ? "Upload Folder" : "Folder Loaded"
	enabled: filesReady
	anchors {
            top: parent.top
	    topMargin: 200
	    horizontalCenter: parent.horizontalCenter
	}
	font {
            family: Theme.fontFamily
	    pointSize: Theme.inputSize
        }
        onClicked: Analysis.select_folder()
	HoverHandler { cursorShape: Qt.PointingHandCursor }
    }

    Button {
        id: runButton
        width: 225; height: 75
        text: "Run"
        enabled: !filesReady
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
        function onVideoUpdated(file) { videoFilePath = file }
        function onCsvUpdated(file) { csvFilePath = file }
    }
}
