import QtQuick
import "../theme"

Item {
    id: root

    property string iconName: "edit"
    property int iconSize: 16
    property int buttonSize: 34
    property string tooltip: ""
    property color iconColor: Theme.textSecondary
    property color hoverIconColor: Theme.primary
    property color hoverBgColor: Theme.surfaceHover

    signal clicked()

    implicitWidth: buttonSize
    implicitHeight: buttonSize

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: Theme.radiusMD
        color: mouseArea.pressed ? Theme.surfaceActive :
               mouseArea.containsMouse ? root.hoverBgColor : "transparent"
        border.color: mouseArea.containsMouse ? Theme.border : "transparent"
        border.width: 1

        Behavior on color { ColorAnimation { duration: Theme.animFast } }

        Icon {
            anchors.centerIn: parent
            name: root.iconName
            size: root.iconSize
            color: mouseArea.containsMouse ? root.hoverIconColor : root.iconColor
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
