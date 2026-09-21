import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property bool isOpen: false
    property string title: "Confirm Action"
    property string message: "Are you sure you want to proceed?"
    property string confirmText: "Confirm"
    property string cancelText: "Cancel"
    property string variant: "danger" // "danger" | "primary" | "warning"
    property string iconName: variant === "danger" ? "trash" : "check"

    signal confirmed()
    signal cancelled()

    anchors.fill: parent
    visible: opacity > 0
    opacity: isOpen ? 1 : 0
    z: 100

    Behavior on opacity { NumberAnimation { duration: Theme.animFast } }

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.6)

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.isOpen = false;
                root.cancelled();
            }
        }
    }

    Rectangle {
        anchors.centerIn: parent
        width: Math.min(420, parent.width - 40)
        implicitHeight: layout.implicitHeight + (Theme.spacingLG * 2)
        radius: Theme.radiusLG
        color: Theme.surface
        border.color: Theme.border
        border.width: 1

        ColumnLayout {
            id: layout
            anchors.fill: parent
            anchors.margins: Theme.spacingLG
            spacing: Theme.spacingMD

            RowLayout {
                spacing: Theme.spacingMD
                Layout.fillWidth: true

                Rectangle {
                    width: 42
                    height: 42
                    radius: 21
                    color: root.variant === "danger" ? Theme.dangerSoft :
                           (root.variant === "warning" ? Theme.warningSoft : Theme.primarySoft)

                    Icon {
                        anchors.centerIn: parent
                        name: root.iconName
                        size: 20
                        color: root.variant === "danger" ? Theme.danger :
                               (root.variant === "warning" ? Theme.warning : Theme.primary)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: root.title
                        color: Theme.textPrimary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontTitle
                        font.weight: Theme.weightBold
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            Text {
                text: root.message
                color: Theme.textSecondary
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontBody
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: Theme.spacingSM
                spacing: Theme.spacingMD

                SecondaryButton {
                    text: root.cancelText
                    Layout.fillWidth: true
                    onClicked: {
                        root.isOpen = false;
                        root.cancelled();
                    }
                }

                PrimaryButton {
                    text: root.confirmText
                    Layout.fillWidth: true
                    customColor: root.variant === "danger" ? Theme.danger : Theme.primary
                    customHoverColor: root.variant === "danger" ? Qt.darker(Theme.danger, 1.15) : Theme.primaryHover
                    onClicked: {
                        root.isOpen = false;
                        root.confirmed();
                    }
                }
            }
        }
    }
}
