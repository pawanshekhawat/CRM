import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

ColumnLayout {
    id: root

    property string label: ""
    property bool required: false
    property string text: ""
    property string placeholder: ""
    property string prefix: ""
    property string suffix: ""
    property bool isMultiline: false
    property int customHeight: isMultiline ? 84 : 40
    property string errorMessage: ""
    property bool readOnly: false

    signal valueModified(string newValue)

    spacing: 6
    Layout.fillWidth: true
    Layout.preferredWidth: 240
    implicitWidth: 240

    RowLayout {
        visible: root.label !== ""
        spacing: 4
        Layout.fillWidth: true

        Text {
            text: root.label
            color: Theme.textSecondary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSmall
            font.weight: Theme.weightMedium
        }

        Text {
            visible: root.required
            text: "*"
            color: Theme.danger
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSmall
            font.weight: Theme.weightBold
        }
    }

    Rectangle {
        Layout.fillWidth: true
        height: root.customHeight
        implicitHeight: root.customHeight
        radius: Theme.radiusMD
        color: root.readOnly ? Theme.surfaceElevated : (input.activeFocus || (textArea && textArea.activeFocus) ? Theme.surfaceElevated : Theme.surface)
        border.color: root.errorMessage !== "" ? Theme.danger :
                      ((input.activeFocus || (textArea && textArea.activeFocus)) ? Theme.borderFocus : Theme.border)
        border.width: 1

        Behavior on color { ColorAnimation { duration: Theme.animFast } }
        Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacingMD
            anchors.rightMargin: Theme.spacingMD
            spacing: Theme.spacingSM

            Text {
                visible: root.prefix !== ""
                text: root.prefix
                color: Theme.textMuted
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontBody
                Layout.alignment: root.isMultiline ? Qt.AlignTop : Qt.AlignVCenter
                Layout.topMargin: root.isMultiline ? 8 : 0
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                TextInput {
                    id: input
                    visible: !root.isMultiline
                    anchors.fill: parent
                    verticalAlignment: TextInput.AlignVCenter
                    text: root.text
                    color: root.readOnly ? Theme.textSecondary : Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontBody
                    selectByMouse: true
                    readOnly: root.readOnly
                    clip: true

                    Text {
                        text: root.placeholder
                        color: Theme.textMuted
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBody
                        visible: !input.text && !input.activeFocus
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    onTextChanged: {
                        if (root.text !== input.text) {
                            root.text = input.text;
                            root.valueModified(input.text);
                        }
                    }
                }

                TextArea {
                    id: textArea
                    visible: root.isMultiline
                    anchors.fill: parent
                    anchors.topMargin: 6
                    anchors.bottomMargin: 6
                    text: root.text
                    color: root.readOnly ? Theme.textSecondary : Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontBody
                    selectByMouse: true
                    readOnly: root.readOnly
                    wrapMode: TextEdit.Wrap
                    background: null

                    Text {
                        text: root.placeholder
                        color: Theme.textMuted
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBody
                        visible: !textArea.text && !textArea.activeFocus
                        anchors.top: parent.top
                        anchors.topMargin: 0
                    }

                    onTextChanged: {
                        if (root.text !== textArea.text) {
                            root.text = textArea.text;
                            root.valueModified(textArea.text);
                        }
                    }
                }
            }

            Text {
                visible: root.suffix !== ""
                text: root.suffix
                color: Theme.textMuted
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSmall
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }

    Text {
        visible: root.errorMessage !== ""
        text: root.errorMessage
        color: Theme.danger
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontCaption
    }
}
