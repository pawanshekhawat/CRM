import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property string text: "Button"
    property string iconName: ""
    property bool loading: false
    property int customHeight: 38
    property color customColor: Theme.primary
    property color customHoverColor: Theme.primaryHover

    signal clicked()

    implicitHeight: customHeight
    implicitWidth: layout.implicitWidth + (Theme.spacingMD * 2)

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: Theme.radiusMD
        color: !root.enabled ? (Theme.isDark ? "#1E293B" : "#E2E8F0") :
               mouseArea.pressed ? Qt.darker(root.customColor, 1.15) :
               mouseArea.containsMouse ? root.customHoverColor : root.customColor

        Behavior on color { ColorAnimation { duration: Theme.animFast } }

        RowLayout {
            id: layout
            anchors.centerIn: parent
            width: Math.min(implicitWidth, parent.width - (Theme.spacingSM * 2))
            spacing: Theme.spacingSM

            Icon {
                id: icon
                visible: root.iconName !== "" && !root.loading
                name: root.iconName
                size: 16
                color: !root.enabled ? Theme.textMuted : "#FFFFFF"
            }

            Text {
                text: root.text
                color: !root.enabled ? Theme.textMuted : "#FFFFFF"
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
        enabled: root.enabled && !root.loading
        hoverEnabled: true
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.clicked()
    }
}
