import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    property string appVersion: "1.0.0"
    property string latestVersion: "1.0.0"
    property bool updateAvailable: false
    property var changelogList: []
    property bool isCheckingUpdate: false
    property bool isDownloadingUpdate: false
    property real downloadPercentage: 0.0

    function init() {
        if (typeof updaterBridge !== "undefined") {
            appVersion = updaterBridge.getCurrentVersion();
        }
    }

    Component.onCompleted: init()

    Connections {
        target: typeof updaterBridge !== "undefined" ? updaterBridge : null

        function onCheckStarted() {
            root.isCheckingUpdate = true;
        }

        function onCheckFinished(available, latestV, title, changelog) {
            root.isCheckingUpdate = false;
            root.updateAvailable = available;
            root.latestVersion = latestV;
            root.changelogList = changelog;
            if (available) {
                crmBridge.showToast(`Version ${latestV} is available!`, "info", "Update Found");
            } else {
                crmBridge.showToast(`You are on the latest version (${root.appVersion}).`, "success", "Up to Date");
            }
        }

        function onDownloadProgress(downloaded, total, pct) {
            root.isDownloadingUpdate = true;
            root.downloadPercentage = pct;
        }

        function onDownloadFinished(filePath) {
            root.isDownloadingUpdate = false;
            crmBridge.showToast("Update downloaded! Applying changes and restarting...", "success", "Applying Update");
        }

        function onUpdateFailed(errMsg) {
            root.isCheckingUpdate = false;
            root.isDownloadingUpdate = false;
            crmBridge.showToast(errMsg, "error", "Update Error");
        }
    }

    Item {
        width: root.availableWidth
        implicitHeight: mainCol.implicitHeight + (Theme.spacingLG * 2)

        ColumnLayout {
            id: mainCol
            anchors.fill: parent
            anchors.margins: Theme.spacingLG
            spacing: Theme.spacingLG

        // Header
        PageHeader {
            title: "System Settings & Diagnostics"
            subtitle: "Manage offline SQLite storage, backups, software updates, and visual theme preferences"
        }

        // Section 1: Software Version & In-App Auto-Updater
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: updateCardLayout.implicitHeight + (Theme.spacingLG * 2)
            radius: Theme.radiusLG
            color: Theme.surface
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                id: updateCardLayout
                anchors.fill: parent
                anchors.margins: Theme.spacingLG
                spacing: Theme.spacingMD

                FormSection {
                    title: "Software Updates & Releases"
                    description: "Check for GitHub release updates and self-install portable updates safely"

                    ColumnLayout {
                        spacing: Theme.spacingMD
                        Layout.fillWidth: true

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingMD

                            ColumnLayout {
                                spacing: 2
                                Text { text: "Installed Version"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                                Text { text: `v${root.appVersion}`; color: Theme.textPrimary; font.pixelSize: Theme.fontTitle; font.weight: Theme.weightBold }
                            }

                            ColumnLayout {
                                visible: root.updateAvailable
                                spacing: 2
                                Text { text: "Latest Available"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                                Text { text: `v${root.latestVersion}`; color: Theme.primaryText; font.pixelSize: Theme.fontTitle; font.weight: Theme.weightBold }
                            }

                            Item { Layout.fillWidth: true }

                            SecondaryButton {
                                text: root.isCheckingUpdate ? "Checking..." : "Check for Updates"
                                iconName: "refresh"
                                enabled: !root.isCheckingUpdate && !root.isDownloadingUpdate
                                onClicked: updaterBridge.checkForUpdates()
                            }

                            PrimaryButton {
                                visible: root.updateAvailable
                                text: root.isDownloadingUpdate ? `Downloading (${Math.round(root.downloadPercentage)}%)...` : "Download & Install Update"
                                iconName: "download"
                                enabled: !root.isDownloadingUpdate
                                onClicked: updaterBridge.downloadAndInstall()
                            }
                        }

                        // Progress Bar if downloading
                        Rectangle {
                            visible: root.isDownloadingUpdate
                            Layout.fillWidth: true
                            height: 8
                            radius: 4
                            color: Theme.surfaceElevated

                            Rectangle {
                                width: (root.downloadPercentage / 100.0) * parent.width
                                height: parent.height
                                radius: 4
                                color: Theme.primary
                            }
                        }

                        // Changelog Box
                        ColumnLayout {
                            visible: root.changelogList.length > 0
                            spacing: 4
                            Layout.fillWidth: true

                            Text {
                                text: "What's New:"
                                color: Theme.textSecondary
                                font.pixelSize: Theme.fontSmall
                                font.weight: Theme.weightBold
                            }

                            Repeater {
                                model: root.changelogList
                                RowLayout {
                                    spacing: 6
                                    Rectangle { width: 4; height: 4; radius: 2; color: Theme.primary; Layout.alignment: Qt.AlignVCenter }
                                    Text { text: modelData; color: Theme.textPrimary; font.pixelSize: Theme.fontSmall }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Section 2: SQLite Database & Backup Safeguards
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: dbCardLayout.implicitHeight + (Theme.spacingLG * 2)
            radius: Theme.radiusLG
            color: Theme.surface
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                id: dbCardLayout
                anchors.fill: parent
                anchors.margins: Theme.spacingLG
                spacing: Theme.spacingMD

                FormSection {
                    title: "SQLite Database & Backup Safeguards"
                    description: "Your local database file crm.db contains all student, course, and fee records"

                    ColumnLayout {
                        spacing: Theme.spacingMD
                        Layout.fillWidth: true

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingMD

                            ColumnLayout {
                                spacing: 2
                                Text { text: "Database Engine"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                                Text { text: "SQLite 3 (Portable & Offline)"; color: Theme.textPrimary; font.pixelSize: Theme.fontBody; font.weight: Theme.weightBold }
                            }

                            ColumnLayout {
                                spacing: 2
                                Text { text: "Storage Location"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                                Text { text: "data/crm.db"; color: Theme.primaryText; font.pixelSize: Theme.fontBody; font.family: Theme.fontMono; font.weight: Theme.weightBold }
                            }

                            Item { Layout.fillWidth: true }

                            SecondaryButton {
                                text: "Open Data Folder in Explorer"
                                iconName: "documents"
                                onClicked: crmBridge.openPathInExplorer("")
                            }

                            PrimaryButton {
                                text: "Create Immediate Backup"
                                iconName: "download"
                                onClicked: crmBridge.createManualBackup()
                            }
                        }

                        Text {
                            text: "• Safe Guarantee: Application updates never overwrite your database or student photos. All updates preserve data/ automatically."
                            color: Theme.textMuted
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSmall
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }

        // Section 3: Visual Theme Preferences
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: themeCardLayout.implicitHeight + (Theme.spacingLG * 2)
            radius: Theme.radiusLG
            color: Theme.surface
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                id: themeCardLayout
                anchors.fill: parent
                anchors.margins: Theme.spacingLG
                spacing: Theme.spacingMD

                FormSection {
                    title: "Visual Theme"
                    description: "Choose between Dark Mode (refined default) and Clean Light Mode"

                    RowLayout {
                        spacing: Theme.spacingMD

                        FilterBar {
                            options: ["Dark Mode", "Light Mode"]
                            selectedOption: Theme.isDark ? "Dark Mode" : "Light Mode"
                            onSelectionChanged: opt => {
                                var mode = (opt === "Dark Mode") ? "dark" : "light";
                                Theme.mode = mode;
                                crmBridge.setThemeMode(mode);
                            }
                        }
                    }
                }
            }
        }
    }
}
}
