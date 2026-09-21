import QtQuick
import "../theme"

Item {
    id: root

    property string name: ""
    property string photoUrl: ""
    property int size: 40

    implicitWidth: size
    implicitHeight: size

    readonly property string initials: {
        if (!name || name.trim() === "") return "?";
        var parts = name.trim().split(" ");
        if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }

    readonly property color bgTone: {
        var colors = [Theme.primarySoft, Theme.accentSoft, Theme.infoSoft, Theme.warningSoft];
        var hash = 0;
        for (var i = 0; i < (name || "").length; i++) hash += name.charCodeAt(i);
        return colors[Math.abs(hash) % colors.length];
    }

    readonly property color textTone: {
        var colors = [Theme.primaryText, Theme.accent, Theme.infoText, Theme.warningText];
        var hash = 0;
        for (var i = 0; i < (name || "").length; i++) hash += name.charCodeAt(i);
        return colors[Math.abs(hash) % colors.length];
    }

    Rectangle {
        anchors.fill: parent
        radius: root.size / 2
        color: root.bgTone
        border.color: Theme.border
        border.width: 1
        clip: true

        Text {
            visible: !photoImage.visible || photoImage.status !== Image.Ready
            anchors.centerIn: parent
            text: root.initials
            color: root.textTone
            font.family: Theme.fontFamily
            font.pixelSize: Math.max(10, Math.floor(root.size * 0.38))
            font.weight: Theme.weightBold
        }

        Image {
            id: photoImage
            anchors.fill: parent
            source: root.photoUrl
            visible: root.photoUrl !== ""
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
        }
    }
}
