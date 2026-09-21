import QtQuick
import QtQuick.Layouts
import "../theme"

Rectangle {
    id: root

    property string organizationName: "CADDESK Centre"
    property string appVersion: "1.0.0"
    property bool hasUpdateAvailable: false

    signal searchSubmitted(string query)
    signal backupClicked()
    signal updateClicked()
    signal themeToggleClicked()
    signal sidebarToggleClicked()

    implicitHeight: 60
    Layout.fillWidth: true
    color: Theme.topBarBackground
    border.color: Theme.topBarBorder
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingMD
        anchors.rightMargin: Theme.spacingLG
        spacing: Theme.spacingMD

        // Global Sidebar Toggle Button
        IconButton {
            iconName: "menu"
            tooltip: "Toggle Sidebar (Ctrl+B)"
            buttonSize: 34
            iconSize: 18
            onClicked: root.sidebarToggleClicked()
        }

        // Global Quick Search
        SearchBar {
            placeholderText: "Search students, courses, staff..."
            implicitWidth: 320
            onSearchChanged: query => root.searchSubmitted(query)
        }

        Item { Layout.fillWidth: true }

        // Live Database Status Indicator
        Rectangle {
            height: 30
            radius: Theme.radiusFull
            color: Theme.surfaceElevated
            border.color: Theme.borderSubtle
            border.width: 1
            implicitWidth: dbStatusRow.implicitWidth + 16

            RowLayout {
                id: dbStatusRow
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    width: 7
                    height: 7
                    radius: 3.5
                    color: Theme.success
                }

                Text {
                    text: "SQLite Connected"
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontCaption
                    font.weight: Theme.weightMedium
                }
            }
        }

        // Manual Backup Action
        SecondaryButton {
            text: "Backup DB"
            iconName: "download"
            customHeight: 34
            onClicked: root.backupClicked()
        }

        // Version & Update Status Button
        Rectangle {
            id: updateBtn
            height: 34
            radius: Theme.radiusMD
            color: root.hasUpdateAvailable ? Theme.warningSoft :
                   (updateMouse.containsMouse ? Theme.surfaceHover : Theme.surface)
            border.color: root.hasUpdateAvailable ? Theme.warning : Theme.border
            border.width: 1
            implicitWidth: updateRow.implicitWidth + 16

            RowLayout {
                id: updateRow
                anchors.centerIn: parent
                spacing: 6

                Icon {
                    name: "refresh"
                    size: 14
                    color: root.hasUpdateAvailable ? Theme.warningText : Theme.textSecondary
                }

                Text {
                    text: root.hasUpdateAvailable ? "Update Available" : `v${root.appVersion}`
                    color: root.hasUpdateAvailable ? Theme.warningText : Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSmall
                    font.weight: Theme.weightMedium
                }
            }

            MouseArea {
                id: updateMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.updateClicked()
            }
        }

        // Theme Toggle (Dark / Light)
        IconButton {
            iconName: Theme.isDark ? "circle" : "settings"
            tooltip: Theme.isDark ? "Switch to Light Mode" : "Switch to Dark Mode"
            buttonSize: 34
            onClicked: root.themeToggleClicked()
        }

        // Organization Avatar / Info
        RowLayout {
            spacing: Theme.spacingSM

            Rectangle {
                width: 34
                height: 34
                radius: 17
                color: Theme.primarySoft
                border.color: Theme.primary
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "CD"
                    color: Theme.primaryText
                    font.family: Theme.fontFamily
                    font.pixelSize: 12
                    font.weight: Theme.weightBold
                }
            }

            ColumnLayout {
                spacing: 0

                Text {
                    text: root.organizationName
                    color: Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontBody
                    font.weight: Theme.weightBold
                }

                Text {
                    text: "Administrator"
                    color: Theme.textMuted
                    font.family: Theme.fontFamily
                    font.pixelSize: 10
                }
            }
        }
    }
}
