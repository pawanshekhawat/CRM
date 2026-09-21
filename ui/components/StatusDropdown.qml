import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property string currentStatus: "Active"
    property var options: ["Active", "Completed", "Dropout"]
    property int customHeight: 26

    signal statusSelected(string newStatus)

    implicitHeight: customHeight
    implicitWidth: 104

    function getStatusBg(statusStr) {
        var s = (statusStr || "").toLowerCase();
        if (s === "active" || s === "paid" || s === "success") return Theme.successSoft;
        if (s === "completed") return Theme.primarySoft;
        if (s === "dropout" || s === "dropped" || s === "inactive") return Theme.dangerSoft;
        if (s === "warning" || s === "partial" || s === "pending") return Theme.warningSoft;
        return Theme.surfaceElevated;
    }

    function getStatusText(statusStr) {
        var s = (statusStr || "").toLowerCase();
        if (s === "active" || s === "paid" || s === "success") return Theme.successText;
        if (s === "completed") return Theme.primaryText;
        if (s === "dropout" || s === "dropped" || s === "inactive") return Theme.dangerText;
        if (s === "warning" || s === "partial" || s === "pending") return Theme.warningText;
        return Theme.textSecondary;
    }

    function getStatusDot(statusStr) {
        var s = (statusStr || "").toLowerCase();
        if (s === "active" || s === "paid" || s === "success") return Theme.success;
        if (s === "completed") return Theme.primary;
        if (s === "dropout" || s === "dropped" || s === "inactive") return Theme.danger;
        if (s === "warning" || s === "partial" || s === "pending") return Theme.warning;
        return Theme.textMuted;
    }

    Rectangle {
        id: badgeBox
        anchors.fill: parent
        radius: Theme.radiusFull
        color: badgeMouse.containsMouse || statusPopup.visible ? Theme.surfaceHover : root.getStatusBg(root.currentStatus)
        border.color: badgeMouse.containsMouse || statusPopup.visible ? Theme.primary : Qt.rgba(root.getStatusDot(root.currentStatus).r, root.getStatusDot(root.currentStatus).g, root.getStatusDot(root.currentStatus).b, 0.4)
        border.width: 1

        Behavior on color { ColorAnimation { duration: Theme.animFast } }
        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            spacing: 5

            Rectangle {
                width: 6
                height: 6
                radius: 3
                color: root.getStatusDot(root.currentStatus)
                Layout.alignment: Qt.AlignVCenter
            }

            Text {
                id: label
                text: root.currentStatus
                color: root.getStatusText(root.currentStatus)
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontCaption
                font.weight: Theme.weightMedium
                elide: Text.ElideRight
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
            }

            Icon {
                name: statusPopup.visible ? "chevron-up" : "chevron-down"
                size: 9
                color: root.getStatusText(root.currentStatus)
                opacity: 0.8
                Layout.alignment: Qt.AlignVCenter
            }
        }

        MouseArea {
            id: badgeMouse
            anchors.fill: parent
            hoverEnabled: root.enabled
            cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: {
                if (root.enabled) {
                    if (statusPopup.visible) {
                        statusPopup.close();
                    } else {
                        statusPopup.open();
                    }
                }
            }
        }
    }

    Popup {
        id: statusPopup
        y: badgeBox.height + 4
        width: 130
        padding: 4
        z: 9999
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        background: Rectangle {
            radius: Theme.radiusMD
            color: Theme.surfaceElevated
            border.color: Theme.border
            border.width: 1
        }

        contentItem: ColumnLayout {
            spacing: 2

            Repeater {
                model: root.options

                Rectangle {
                    id: optItem
                    Layout.fillWidth: true
                    implicitHeight: 28
                    radius: Theme.radiusSM
                    color: optMouse.containsMouse ? Theme.surfaceHover :
                           (root.currentStatus === modelData ? Theme.primarySoft : "transparent")

                    readonly property bool isSelected: root.currentStatus === modelData

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        spacing: 6

                        Rectangle {
                            width: 6
                            height: 6
                            radius: 3
                            color: root.getStatusDot(modelData)
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Text {
                            text: modelData
                            color: optItem.isSelected ? Theme.primaryText :
                                   (optMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary)
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSmall
                            font.weight: optItem.isSelected ? Theme.weightDemiBold : Theme.weightNormal
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Icon {
                            visible: optItem.isSelected
                            name: "check"
                            size: 11
                            color: Theme.primary
                            Layout.alignment: Qt.AlignVCenter
                        }
                    }

                    MouseArea {
                        id: optMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            statusPopup.close();
                            if (modelData !== root.currentStatus) {
                                root.statusSelected(modelData);
                            }
                        }
                    }
                }
            }
        }
    }
}
