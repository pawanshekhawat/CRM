import QtQuick
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property string iconName: "search"
    property string title: "No Records Found"
    property string message: "There are no records matching your current filter criteria."
    property string buttonText: ""
    property string buttonIcon: "refresh"

    signal actionClicked()

    implicitWidth: 320
    implicitHeight: layout.implicitHeight + (Theme.spacingXL * 2)

    ColumnLayout {
        id: layout
        anchors.centerIn: parent
        spacing: Theme.spacingMD
        width: Math.min(parent.width - 32, 380)

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 56
            height: 56
            radius: 28
            color: Theme.surfaceElevated
            border.color: Theme.border
            border.width: 1

            Icon {
                anchors.centerIn: parent
                name: root.iconName
                size: 26
                color: Theme.textMuted
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.title
            color: Theme.textPrimary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontTitle
            font.weight: Theme.weightDemiBold
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }

        Text {
            Layout.fillWidth: true
            text: root.message
            color: Theme.textSecondary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontBody
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }

        SecondaryButton {
            visible: root.buttonText !== ""
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: Theme.spacingSM
            text: root.buttonText
            iconName: root.buttonIcon
            onClicked: root.actionClicked()
        }
    }
}
