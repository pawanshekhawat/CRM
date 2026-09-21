import QtQuick
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: root

    property string title: "Metric"
    property string value: "0"
    property string subtext: ""
    property string iconName: "chart"
    property color iconColor: Theme.primary
    property color iconBgColor: Theme.primarySoft
    property string trendText: ""
    property bool isPositiveTrend: true

    Layout.fillWidth: true
    implicitHeight: 110
    radius: Theme.radiusLG
    color: mouseArea.containsMouse ? Theme.surfaceElevated : Theme.surface
    border.color: mouseArea.containsMouse ? Theme.borderFocus : Theme.border
    border.width: 1

    Behavior on color { ColorAnimation { duration: Theme.animFast } }
    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMD
        spacing: Theme.spacingMD

        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            spacing: 4

            Text {
                text: root.title
                color: Theme.textSecondary
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSmall
                font.weight: Theme.weightMedium
                elide: Text.ElideRight
                Layout.fillWidth: true
            }

            Text {
                text: root.value
                color: Theme.textPrimary
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontDisplay
                font.weight: Theme.weightBold
                elide: Text.ElideRight
                Layout.fillWidth: true
            }

            RowLayout {
                visible: root.subtext !== "" || root.trendText !== ""
                spacing: 6
                Layout.fillWidth: true

                Rectangle {
                    visible: root.trendText !== ""
                    height: 18
                    radius: Theme.radiusSM
                    Layout.preferredWidth: trendLabel.implicitWidth + 8
                    Layout.preferredHeight: 18
                    color: root.isPositiveTrend ? Theme.successSoft : Theme.dangerSoft

                    Text {
                        id: trendLabel
                        anchors.centerIn: parent
                        text: root.trendText
                        color: root.isPositiveTrend ? Theme.successText : Theme.dangerText
                        font.family: Theme.fontFamily
                        font.pixelSize: 10
                        font.weight: Theme.weightBold
                    }
                }

                Text {
                    visible: root.subtext !== ""
                    text: root.subtext
                    color: Theme.textMuted
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontCaption
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
            }
        }

        Rectangle {
            Layout.alignment: Qt.AlignVCenter
            width: 46
            height: 46
            radius: Theme.radiusMD
            color: root.iconBgColor

            Icon {
                anchors.centerIn: parent
                name: root.iconName
                size: 22
                color: root.iconColor
            }
        }
    }
}
