import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: root

    property string placeholderText: "Search records..."
    property string text: ""
    property int debounceMs: 250

    signal searchChanged(string query)

    implicitHeight: 38
    implicitWidth: 280
    radius: Theme.radiusMD
    color: input.activeFocus ? Theme.surfaceElevated : Theme.surface
    border.color: input.activeFocus ? Theme.borderFocus : Theme.border
    border.width: 1

    Behavior on color { ColorAnimation { duration: Theme.animFast } }
    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

    Timer {
        id: debounceTimer
        interval: root.debounceMs
        repeat: false
        onTriggered: {
            root.text = input.text;
            root.searchChanged(input.text);
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingSM + 4
        anchors.rightMargin: Theme.spacingSM
        spacing: Theme.spacingSM

        Icon {
            name: "search"
            size: 15
            color: input.activeFocus ? Theme.primary : Theme.textMuted
            Layout.alignment: Qt.AlignVCenter
        }

        TextInput {
            id: input
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            color: Theme.textPrimary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontBody
            selectByMouse: true
            clip: true

            Text {
                text: root.placeholderText
                color: Theme.textMuted
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontBody
                visible: !input.text && !input.activeFocus
                anchors.verticalCenter: parent.verticalCenter
            }

            onTextChanged: {
                debounceTimer.restart();
            }

            onAccepted: {
                debounceTimer.stop();
                root.text = input.text;
                root.searchChanged(input.text);
            }
        }

        IconButton {
            visible: input.text.length > 0
            iconName: "close"
            iconSize: 12
            buttonSize: 24
            Layout.alignment: Qt.AlignVCenter
            onClicked: {
                input.text = "";
                input.forceActiveFocus();
                debounceTimer.stop();
                root.text = "";
                root.searchChanged("");
            }
        }
    }
}
