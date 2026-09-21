import QtQuick
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property string text: "Cancel"
    property string iconName: ""
    property int customHeight: 38
    property color textColor: Theme.textPrimary

    signal clicked()

    implicitHeight: customHeight
    implicitWidth: layout.implicitWidth + (Theme.spacingMD * 2)

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: Theme.radiusMD
        color: mouseArea.pressed ? Theme.surfaceActive :
               mouseArea.containsMouse ? Theme.surfaceHover : Theme.surface
        border.color: mouseArea.containsMouse ? Theme.borderFocus : Theme.border
        border.width: 1

        Behavior on color { ColorAnimation { duration: Theme.animFast } }
        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

        RowLayout {
            id: layout
            anchors.centerIn: parent
            width: Math.min(implicitWidth, parent.width - (Theme.spacingSM * 2))
            spacing: Theme.spacingSM

            Icon {
                id: icon
                visible: root.iconName !== ""
                name: root.iconName
                size: 15
                color: !root.enabled ? Theme.textMuted : root.textColor
            }

            Text {
                text: root.text
                color: !root.enabled ? Theme.textMuted : root.textColor
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontBody
                font.weight: Theme.weightMedium
                elide: Text.ElideRight
                Layout.fillWidth: true
                horizontalAlignment: root.iconName !== "" ? Text.AlignLeft : Text.AlignHCenter
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: root.enabled
        hoverEnabled: true
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.clicked()
    }
}
