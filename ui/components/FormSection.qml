import QtQuick
import QtQuick.Layouts
import "../theme"

ColumnLayout {
    id: root

    property string title: "Section Title"
    property string description: ""
    default property alias content: contentContainer.data

    spacing: Theme.spacingMD
    Layout.fillWidth: true

    ColumnLayout {
        spacing: 2
        Layout.fillWidth: true

        Text {
            text: root.title
            color: Theme.textPrimary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontTitle
            font.weight: Theme.weightDemiBold
        }

        Text {
            visible: root.description !== ""
            text: root.description
            color: Theme.textMuted
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSmall
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.topMargin: 4
            height: 1
            color: Theme.borderSubtle
        }
    }

    ColumnLayout {
        id: contentContainer
        Layout.fillWidth: true
        spacing: Theme.spacingMD
    }
}
