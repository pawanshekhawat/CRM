import QtQuick
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property var items: []

    implicitWidth: 300
    implicitHeight: layout.implicitHeight

    ColumnLayout {
        id: layout
        anchors.fill: parent
        spacing: 0

        Repeater {
            model: root.items

            Item {
                Layout.fillWidth: true
                implicitHeight: itemRow.implicitHeight + 16

                RowLayout {
                    id: itemRow
                    anchors.fill: parent
                    anchors.topMargin: 4
                    spacing: Theme.spacingMD

                    // Timeline node + connector line
                    Item {
                        width: 20
                        Layout.fillHeight: true

                        // Connector line
                        Rectangle {
                            visible: index < (root.items.length - 1)
                            anchors.top: dot.bottom
                            anchors.bottom: parent.bottom
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: 2
                            color: Theme.borderSubtle
                        }

                        // Dot
                        Rectangle {
                            id: dot
                            anchors.top: parent.top
                            anchors.topMargin: 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: 10
                            height: 10
                            radius: 5
                            color: modelData.color || Theme.primary
                            border.color: Theme.surface
                            border.width: 1
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        RowLayout {
                            Layout.fillWidth: true

                            Text {
                                text: modelData.title || ""
                                color: Theme.textPrimary
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontBody
                                font.weight: Theme.weightMedium
                                Layout.fillWidth: true
                            }

                            Text {
                                text: modelData.time || ""
                                color: Theme.textMuted
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontCaption
                            }
                        }

                        Text {
                            visible: modelData.description !== undefined && modelData.description !== ""
                            text: modelData.description || ""
                            color: Theme.textSecondary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSmall
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
    }
}
