import QtQuick
import "../theme"

Item {
    id: root

    property string status: "Active"
    property string text: status
    property int customHeight: 24

    implicitHeight: customHeight
    implicitWidth: label.implicitWidth + (Theme.spacingSM * 2) + 12

    readonly property color badgeBg: {
        var s = (root.status || "").toLowerCase();
        if (s.indexOf("paid") >= 0 || s === "active" || s === "completed" || s === "success") return Theme.successSoft;
        if (s.indexOf("partial") >= 0 || s === "warning" || s === "in progress" || s === "upcoming") return Theme.warningSoft;
        if (s.indexOf("pending") >= 0 || s.indexOf("overdue") >= 0 || s === "failed" || s === "danger" || s === "inactive" || s === "dropped") return Theme.dangerSoft;
        if (s.indexOf("enrolled") >= 0 || s === "info") return Theme.infoSoft;
        return Theme.surfaceElevated;
    }

    readonly property color badgeText: {
        var s = (root.status || "").toLowerCase();
        if (s.indexOf("paid") >= 0 || s === "active" || s === "completed" || s === "success") return Theme.successText;
        if (s.indexOf("partial") >= 0 || s === "warning" || s === "in progress" || s === "upcoming") return Theme.warningText;
        if (s.indexOf("pending") >= 0 || s.indexOf("overdue") >= 0 || s === "failed" || s === "danger" || s === "inactive" || s === "dropped") return Theme.dangerText;
        if (s.indexOf("enrolled") >= 0 || s === "info") return Theme.infoText;
        return Theme.textSecondary;
    }

    readonly property color dotColor: {
        var s = (root.status || "").toLowerCase();
        if (s.indexOf("paid") >= 0 || s === "active" || s === "completed" || s === "success") return Theme.success;
        if (s.indexOf("partial") >= 0 || s === "warning" || s === "in progress" || s === "upcoming") return Theme.warning;
        if (s.indexOf("pending") >= 0 || s.indexOf("overdue") >= 0 || s === "failed" || s === "danger" || s === "inactive" || s === "dropped") return Theme.danger;
        if (s.indexOf("enrolled") >= 0 || s === "info") return Theme.info;
        return Theme.textMuted;
    }

    Rectangle {
        anchors.fill: parent
        radius: Theme.radiusFull
        color: root.badgeBg
        border.color: Qt.rgba(root.dotColor.r, root.dotColor.g, root.dotColor.b, 0.25)
        border.width: 1

        Row {
            anchors.centerIn: parent
            spacing: 6

            Rectangle {
                width: 6
                height: 6
                radius: 3
                color: root.dotColor
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                id: label
                text: root.text
                color: root.badgeText
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontCaption
                font.weight: Theme.weightMedium
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
