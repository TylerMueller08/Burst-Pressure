// AnalysisScreen.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

Item {
    id: screen
    anchors.fill: parent

    signal goBack()

    ColumnLayout {
        anchors.fill: parent
        spacing: 8
        padding: 12

        RowLayout {
            spacing: 8
            Button { text: "Open Video"; onClicked: analyzer.openFileDialog() }
            Button { text: "Preview Frame 0"; onClicked: analyzer.preview_frame(0) }
            Button { text: "Run Analysis"; onClicked: analyzer.run_analysis() }
            Button { text: "Cancel"; onClicked: analyzer.cancel() }
            Button { text: "Export CSV"; onClicked:
                {
                    // Example: you should provide a dialog to pick out path; for demo use data folder
                    var out = Qt.resolvedUrl("data/analysis_export.csv")
                    analyzer.export_csv(out)
                }
            }
            Button { text: "Export Annotated Video"; onClicked:
                {
                    var out = Qt.resolvedUrl("data/analysis_annotated.mp4")
                    analyzer.export_annotated_video(out)
                }
            }
            Button { text: "< Back"; onClicked: goBack() }
        }

        RowLayout {
            spacing: 8
            Image {
                id: preview
                source: analyzer.frameData // data:image/png;base64,...
                width: 640
                height: 360
                fillMode: Image.PreserveAspectFit
                visible: true
            }

            ColumnLayout {
                spacing: 6
                Label { text: "Detection Parameters"; font.bold: true }
                Slider { id: sLow; from: 0; to: 200; value: 30
                    onValueChanged: analyzer.low_canny = Math.round(value)
                }
                Label { text: "Low Canny: " + Math.round(analyzer.low_canny) }
                Slider { id: sHigh; from: 0; to: 400; value: 100
                    onValueChanged: analyzer.high_canny = Math.round(value)
                }
                Label { text: "High Canny: " + Math.round(analyzer.high_canny) }
                Slider { id: sCLAHE; from: 1; to: 10; value: 2.0; stepSize: 0.1
                    onValueChanged: analyzer.clahe_clip = value
                }
                Label { text: "CLAHE clip: " + analyzer.clahe_clip.toFixed(1) }

                RowLayout { spacing: 6
                    Label { text: "Blur ksize" }
                    SpinBox { from:1; to:31; value: analyzer.blur_ksize; stepSize:2
                        onValueChanged: analyzer.blur_ksize = value
                    }
                }

                RowLayout { spacing: 6
                    Label { text: "Sample step (frames)" }
                    SpinBox { from:1; to:30; value: analyzer.sample_frame_step
                        onValueChanged: analyzer.sample_frame_step = value
                    }
                }

                Label { text: "Status:" }
                Text { text: "" }
            }
        }

        ProgressBar {
            id: p
            from: 0; to: 100
            value: 0
            anchors.horizontalCenter: parent.horizontalCenter
        }

        // wire progressChanged to progress bar
        Connections {
            target: analyzer
            onProgressChanged: p.value = arguments[0]
            onLogMessage: console.log("Analyzer:", arguments[0])
            onFrameReady: preview.source = arguments[0]
        }
    }
}
