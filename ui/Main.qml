import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "theme"
import "components"
import "pages"

ApplicationWindow {
    id: window

    visible: true
    width: 1366
    height: 820
    minimumWidth: 1280
    minimumHeight: 720
    title: `${crmBridge ? crmBridge.getAppName() : "Personal CRM"} - ${crmBridge ? crmBridge.getOrganizationName() : "Institute Edition"} (v${crmBridge ? crmBridge.getAppVersion() : "1.0.0"})`
    color: Theme.background

    property string currentPage: "Dashboard"

    Connections {
        target: typeof crmBridge !== "undefined" ? crmBridge : null

        function onPageChanged(pageName) {
            window.currentPage = pageName;
        }

        function onToastMessage(message, msgType, title) {
            globalToast.show(message, msgType, title);
        }

        function onThemeChanged(mode) {
            Theme.mode = mode;
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // App TopBar
        AppTopBar {
            id: topBar
            organizationName: crmBridge ? crmBridge.getOrganizationName() : "CADDESK Centre"
            appVersion: crmBridge ? crmBridge.getAppVersion() : "1.0.0"

            onSearchSubmitted: query => {
                if (query.trim() !== "") {
                    window.currentPage = "Students";
                    studentsPage.searchQuery = query;
                    studentsPage.refresh();
                }
            }

            onBackupClicked: {
                crmBridge.createManualBackup();
            }

            onUpdateClicked: {
                window.currentPage = "Settings";
            }

            onThemeToggleClicked: {
                var nextMode = Theme.isDark ? "light" : "dark";
                Theme.mode = nextMode;
                crmBridge.setThemeMode(nextMode);
            }

            onSidebarToggleClicked: {
                sidebar.isCollapsed = !sidebar.isCollapsed;
            }
        }

        Shortcut {
            sequence: "Ctrl+B"
            onActivated: sidebar.isCollapsed = !sidebar.isCollapsed
        }

        // Main Shell Body: Sidebar + Dynamic Page Stack
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Collapsible Sidebar
            AppSidebar {
                id: sidebar
                Layout.fillHeight: true
                Layout.preferredWidth: isCollapsed ? 64 : 250
                currentPage: window.currentPage
                isCollapsed: false
                onPageSelected: pageName => {
                    window.currentPage = pageName;
                    crmBridge.navigateTo(pageName);
                }
                onToggleCollapse: {
                    isCollapsed = !isCollapsed;
                }
            }

            // Central Page Stack
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Theme.background

                StackLayout {
                    id: pageStack
                    anchors.fill: parent
                    currentIndex: {
                        switch (window.currentPage) {
                            case "Dashboard": return 0;
                            case "Students": return 1;
                            case "StudentDetails": return 2;
                            case "Admissions": return 3;
                            case "Courses": return 4;
                            case "Batches": return 5;
                            case "Fees": return 6;
                            case "Staff": return 7;
                            case "Communications": return 8;
                            case "Reports": return 9;
                            case "Documents": return 10;
                            case "Settings": return 11;
                            default: return 0;
                        }
                    }

                    Dashboard { id: dashboardPage }
                    Students { id: studentsPage }
                    StudentDetails { id: studentDetailsPage }
                    Admissions { id: admissionsPage }
                    Courses { id: coursesPage }
                    Batches { id: batchesPage }
                    Fees { id: feesPage }
                    Staff { id: staffPage }
                    Communications { id: communicationsPage }
                    Reports { id: reportsPage }
                    Documents { id: documentsPage }
                    Settings { id: settingsPage }
                }
            }
        }
    }

    // Global Floating Toast
    Toast {
        id: globalToast
    }
}
