import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Item {
    id: root

    property bool isOpen: false
    property string title: "Drawer Panel"
    property string subtitle: ""
    property int drawerWidth: 480
    property string primaryActionText: "Save Changes"
    property string secondaryActionText: "Cancel"
    property bool showFooter: true
    property bool isPrimaryLoading: false

    default property alias bodyContent: bodyContainer.children

    signal closed()
    signal primaryClicked()
    signal secondaryClicked()

    anchors.fill: parent
    visible: opacity > 0
    opacity: isOpen ? 1 : 0
    z: 99

    Behavior on opacity { NumberAnimation { duration: Theme.animNormal } }

    // Backdrop
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.55)

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.isOpen = false;
                root.closed();
            }
        }
    }

    // Drawer Surface
    Rectangle {
        id: panel
        width: Math.min(root.drawerWidth, root.width * 0.9)
        height: root.height
        anchors.right: parent.right
        x: root.isOpen ? (root.width - width) : root.width
        color: Theme.surface
        border.color: Theme.border
        border.width: 1

        Behavior on x { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutCubic } }

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // Header
            Rectangle {
                Layout.fillWidth: true
                height: 64
                color: Theme.surfaceElevated
                border.color: Theme.borderSubtle
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacingLG
                    anchors.rightMargin: Theme.spacingMD
                    spacing: Theme.spacingMD

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: root.title
                            color: Theme.textPrimary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontTitle
                            font.weight: Theme.weightBold
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }

                        Text {
                            visible: root.subtitle !== ""
                            text: root.subtitle
                            color: Theme.textMuted
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSmall
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }

                    IconButton {
                        iconName: "close"
                        iconSize: 16
                        buttonSize: 34
                        onClicked: {
                            root.isOpen = false;
                            root.closed();
                        }
                    }
                }
            }

            // Scrollable Body
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                Item {
                    id: bodyContainer
                    width: panel.width
                    implicitHeight: childrenRect.height + (Theme.spacingLG * 2)

                    // Add padding around content
                    anchors.margins: Theme.spacingLG
                }
            }

            // Footer
            Rectangle {
                visible: root.showFooter
                Layout.fillWidth: true
                height: 64
                color: Theme.surfaceElevated
                border.color: Theme.borderSubtle
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacingLG
                    anchors.rightMargin: Theme.spacingLG
                    spacing: Theme.spacingMD

                    SecondaryButton {
                        text: root.secondaryActionText
                        onClicked: {
                            root.secondaryClicked();
                            root.isOpen = false;
                            root.closed();
                        }
                    }

                    Item { Layout.fillWidth: true }

                    PrimaryButton {
                        text: root.primaryActionText
                        loading: root.isPrimaryLoading
                        onClicked: root.primaryClicked()
                    }
                }
            }
        }
    }
}
