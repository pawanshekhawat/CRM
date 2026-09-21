import QtQuick
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property string title: "Page Title"
    property string subtitle: ""
    property string countText: ""
    default property alias actions: actionContainer.children

    implicitHeight: 64
    Layout.fillWidth: true

    RowLayout {
        anchors.fill: parent
        spacing: Theme.spacingMD

        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            spacing: 2

            RowLayout {
                spacing: Theme.spacingSM

                Text {
                    text: root.title
                    color: Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontHeader
                    font.weight: Theme.weightBold
                }

                Rectangle {
                    visible: root.countText !== ""
                    height: 22
                    radius: Theme.radiusFull
                    color: Theme.surfaceElevated
                    border.color: Theme.border
                    border.width: 1
                    implicitWidth: countLabel.implicitWidth + 14

                    Text {
                        id: countLabel
                        anchors.centerIn: parent
                        text: root.countText
                        color: Theme.textSecondary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontCaption
                        font.weight: Theme.weightMedium
                    }
                }
            }

            Text {
                visible: root.subtitle !== ""
                text: root.subtitle
                color: Theme.textMuted
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSmall
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }

        RowLayout {
            id: actionContainer
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.spacingSM
        }
    }
}
