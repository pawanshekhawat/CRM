import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: root

    property string currentPage: "Dashboard"
    property bool isCollapsed: false

    signal pageSelected(string pageName)
    signal toggleCollapse()

    implicitWidth: isCollapsed ? 64 : 250
    color: Theme.sidebarBackground
    border.color: Theme.sidebarBorder
    border.width: 1

    Behavior on implicitWidth { NumberAnimation { duration: Theme.animNormal; easing.type: Easing.OutCubic } }

    readonly property var navigationSections: [
        {
            "category": "WORKSPACE",
            "items": [
                { "name": "Dashboard", "label": "Dashboard", "icon": "dashboard" }
            ]
        },
        {
            "category": "STUDENTS",
            "items": [
                { "name": "Students", "label": "All Students", "icon": "students" },
                { "name": "Admissions", "label": "New Admission", "icon": "plus" }
            ]
        },
        {
            "category": "ACADEMICS",
            "items": [
                { "name": "Courses", "label": "Course Catalog", "icon": "courses" },
                { "name": "Batches", "label": "Batches & Schedule", "icon": "batches" }
            ]
        },
        {
            "category": "FINANCE",
            "items": [
                { "name": "Fees", "label": "Fees & Payments", "icon": "fees" }
            ]
        },
        {
            "category": "PEOPLE",
            "items": [
                { "name": "Staff", "label": "Staff Directory", "icon": "staff" }
            ]
        },
        {
            "category": "COMMUNICATION",
            "items": [
                { "name": "Communications", "label": "Message Automation", "icon": "messaging" }
            ]
        },
        {
            "category": "OPERATIONS",
            "items": [
                { "name": "Documents", "label": "Student Documents", "icon": "documents" },
                { "name": "Reports", "label": "Reports & Analytics", "icon": "reports" }
            ]
        },
        {
            "category": "SYSTEM",
            "items": [
                { "name": "Settings", "label": "Settings & Backup", "icon": "settings" }
            ]
        }
    ]

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // App Logo / Brand Header (Clickable in collapsed mode to expand)
        Rectangle {
            id: brandHeader
            Layout.fillWidth: true
            height: 60
            color: root.isCollapsed && headerMouse.containsMouse ? Theme.surfaceHover : "transparent"
            border.color: Theme.borderSubtle
            border.width: 1

            Behavior on color { ColorAnimation { duration: Theme.animFast } }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: root.isCollapsed ? 0 : Theme.spacingMD
                anchors.rightMargin: root.isCollapsed ? 0 : Theme.spacingSM
                spacing: Theme.spacingSM

                Rectangle {
                    id: logoBox
                    width: 34
                    height: 34
                    radius: Theme.radiusMD
                    color: headerMouse.containsMouse && root.isCollapsed ? Theme.primaryDark : Theme.primary
                    Layout.alignment: root.isCollapsed ? Qt.AlignHCenter : Qt.AlignVCenter

                    Behavior on color { ColorAnimation { duration: Theme.animFast } }

                    Icon {
                        anchors.centerIn: parent
                        name: root.isCollapsed && headerMouse.containsMouse ? "chevron-right" : "book"
                        size: 18
                        color: "#FFFFFF"
                    }
                }

                ColumnLayout {
                    visible: !root.isCollapsed
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 0
                    clip: true

                    Text {
                        text: "PERSONAL CRM"
                        color: Theme.textPrimary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBody
                        font.weight: Theme.weightBold
                        elide: Text.ElideRight
                    }

                    Text {
                        text: "Institute Edition"
                        color: Theme.primaryText
                        font.family: Theme.fontFamily
                        font.pixelSize: 10
                        font.weight: Theme.weightMedium
                        elide: Text.ElideRight
                    }
                }

                IconButton {
                    visible: !root.isCollapsed
                    iconName: "chevron-left"
                    iconSize: 14
                    buttonSize: 28
                    tooltip: "Collapse Sidebar"
                    onClicked: root.toggleCollapse()
                }
            }

            MouseArea {
                id: headerMouse
                anchors.fill: parent
                enabled: root.isCollapsed
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.toggleCollapse()
            }
        }

        // Navigation Menu (Scrollable)
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ColumnLayout {
                width: root.isCollapsed ? 64 : 250
                spacing: root.isCollapsed ? 6 : Theme.spacingSM
                Layout.topMargin: Theme.spacingSM
                Layout.bottomMargin: Theme.spacingSM

                Repeater {
                    model: root.navigationSections

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        // Category Heading
                        Text {
                            visible: !root.isCollapsed
                            text: modelData.category
                            color: Theme.textMuted
                            font.family: Theme.fontFamily
                            font.pixelSize: 10
                            font.weight: Theme.weightBold
                            Layout.leftMargin: Theme.spacingMD + 4
                            Layout.topMargin: Theme.spacingSM
                            Layout.bottomMargin: 2
                        }

                        // Nav Items
                        Repeater {
                            model: modelData.items

                            Rectangle {
                                id: navItem
                                readonly property bool isSelected: root.currentPage === modelData.name
                                Layout.fillWidth: true
                                Layout.leftMargin: 8
                                Layout.rightMargin: 8
                                height: 38
                                radius: Theme.radiusMD
                                color: isSelected ? Theme.sidebarActiveBackground :
                                       (navMouse.containsMouse ? Theme.surfaceHover : "transparent")

                                Behavior on color { ColorAnimation { duration: Theme.animFast } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: root.isCollapsed ? 0 : 8
                                    anchors.rightMargin: root.isCollapsed ? 0 : 8
                                    spacing: 10

                                    // Left Active indicator pill (expanded only)
                                    Rectangle {
                                        visible: navItem.isSelected && !root.isCollapsed
                                        width: 3
                                        height: 18
                                        radius: 1.5
                                        color: Theme.sidebarActiveIndicator
                                        Layout.alignment: Qt.AlignVCenter
                                    }

                                    // Icon (centered if collapsed)
                                    Item {
                                        Layout.preferredWidth: root.isCollapsed ? parent.width : 22
                                        Layout.fillHeight: true
                                        Layout.alignment: root.isCollapsed ? Qt.AlignHCenter : Qt.AlignVCenter

                                        Icon {
                                            anchors.centerIn: parent
                                            name: modelData.icon
                                            size: 18
                                            color: navItem.isSelected ? Theme.primary :
                                                   (navMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary)
                                        }
                                    }

                                    Text {
                                        visible: !root.isCollapsed
                                        Layout.fillWidth: true
                                        Layout.alignment: Qt.AlignVCenter
                                        text: modelData.label
                                        color: navItem.isSelected ? Theme.textPrimary :
                                               (navMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary)
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontBody
                                        font.weight: navItem.isSelected ? Theme.weightDemiBold : Theme.weightNormal
                                        elide: Text.ElideNone
                                    }
                                }

                                MouseArea {
                                    id: navMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.pageSelected(modelData.name)
                                }
                            }
                        }
                    }
                }
            }
        }

        // Bottom Collapse / Expand Bar
        Rectangle {
            Layout.fillWidth: true
            height: 44
            color: bottomToggleMouse.containsMouse ? Theme.surfaceHover : "transparent"
            border.color: Theme.borderSubtle
            border.width: 1

            Behavior on color { ColorAnimation { duration: Theme.animFast } }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: root.isCollapsed ? 0 : 16
                anchors.rightMargin: root.isCollapsed ? 0 : 16
                spacing: 10

                Item {
                    Layout.preferredWidth: root.isCollapsed ? parent.width : 22
                    Layout.fillHeight: true
                    Layout.alignment: root.isCollapsed ? Qt.AlignHCenter : Qt.AlignVCenter

                    Icon {
                        anchors.centerIn: parent
                        name: root.isCollapsed ? "chevron-right" : "chevron-left"
                        size: 16
                        color: bottomToggleMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary
                    }
                }

                Text {
                    visible: !root.isCollapsed
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    text: "Collapse sidebar"
                    color: bottomToggleMouse.containsMouse ? Theme.textPrimary : Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontCaption
                    font.weight: Theme.weightMedium
                }
            }

            MouseArea {
                id: bottomToggleMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.toggleCollapse()
            }
        }
    }
}
