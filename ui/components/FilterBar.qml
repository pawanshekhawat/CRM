import QtQuick
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property var options: ["All", "Active", "Pending", "Completed"]
    property string selectedOption: options.length > 0 ? options[0] : "All"

    signal selectionChanged(string option)

    implicitHeight: 38
    implicitWidth: Math.min(chipRow.implicitWidth, 600)
    Layout.fillWidth: true

    Flickable {
        id: flick
        anchors.fill: parent
        contentWidth: chipRow.implicitWidth
        contentHeight: parent.height
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        flickableDirection: Flickable.HorizontalFlick

        WheelHandler {
            target: flick
            onWheel: (event) => {
                var delta = event.angleDelta.y !== 0 ? event.angleDelta.y : event.angleDelta.x;
                flick.contentX = Math.max(0, Math.min(flick.contentWidth - flick.width, flick.contentX - delta));
            }
        }

        Row {
            id: chipRow
            height: parent.height
            spacing: 6

            Repeater {
                model: root.options

                Rectangle {
                    id: chip
                    readonly property bool isSelected: root.selectedOption === modelData
                    height: 34
                    anchors.verticalCenter: parent.verticalCenter
                    implicitWidth: label.implicitWidth + (Theme.spacingMD * 2)
                    radius: Theme.radiusMD
                    color: isSelected ? Theme.primarySoft :
                           (mouseArea.containsMouse ? Theme.surfaceHover : Theme.surfaceElevated)
                    border.color: isSelected ? Theme.primary : Theme.border
                    border.width: 1

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }
                    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

                    Text {
                        id: label
                        anchors.centerIn: parent
                        text: modelData
                        color: chip.isSelected ? Theme.primaryText :
                               (mouseArea.containsMouse ? Theme.textPrimary : Theme.textSecondary)
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSmall
                        font.weight: chip.isSelected ? Theme.weightDemiBold : Theme.weightNormal
                    }

                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            root.selectedOption = modelData;
                            root.selectionChanged(modelData);
                        }
                    }
                }
            }
        }
    }
}
