import QtQuick
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property string message: ""
    property string title: ""
    property string msgType: "info" // "success" | "error" | "warning" | "info"
    property bool visibleState: false

    function show(msg, type, heading) {
        root.message = msg;
        root.msgType = type || "info";
        root.title = heading || (type === "success" ? "Success" : (type === "error" ? "Error" : (type === "warning" ? "Notice" : "Information")));
        root.visibleState = true;
        dismissTimer.restart();
    }

    Timer {
        id: dismissTimer
        interval: 4000
        repeat: false
        onTriggered: root.visibleState = false
    }

    z: 200
    width: 360
    implicitHeight: toastBox.implicitHeight
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    anchors.margins: Theme.spacingLG

    Rectangle {
        id: toastBox
        width: parent.width
        implicitHeight: layout.implicitHeight + (Theme.spacingMD * 2)
        radius: Theme.radiusMD
        color: Theme.surface
        border.color: root.msgType === "success" ? Theme.success :
                      (root.msgType === "error" ? Theme.danger :
                      (root.msgType === "warning" ? Theme.warning : Theme.info))
        border.width: 1

        opacity: root.visibleState ? 1 : 0
        y: root.visibleState ? 0 : 20

        Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }
        Behavior on y { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutCubic } }

        RowLayout {
            id: layout
            anchors.fill: parent
            anchors.margins: Theme.spacingMD
            spacing: Theme.spacingMD

            Rectangle {
                width: 32
                height: 32
                radius: 16
                color: root.msgType === "success" ? Theme.successSoft :
                       (root.msgType === "error" ? Theme.dangerSoft :
                       (root.msgType === "warning" ? Theme.warningSoft : Theme.infoSoft))

                Icon {
                    anchors.centerIn: parent
                    name: root.msgType === "success" ? "check" :
                          (root.msgType === "error" ? "close" :
                          (root.msgType === "warning" ? "circle" : "circle"))
                    size: 16
                    color: root.msgType === "success" ? Theme.success :
                           (root.msgType === "error" ? Theme.danger :
                           (root.msgType === "warning" ? Theme.warning : Theme.info))
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    text: root.title
                    color: Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSmall
                    font.weight: Theme.weightBold
                }

                Text {
                    text: root.message
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSmall
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            IconButton {
                iconName: "close"
                iconSize: 12
                buttonSize: 24
                onClicked: root.visibleState = false
            }
        }
    }
}
