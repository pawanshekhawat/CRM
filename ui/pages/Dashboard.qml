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

    property var globalStats: ({})
    property var financeStats: ({})

    function refresh() {
        if (typeof crmBridge !== "undefined") {
            globalStats = crmBridge.getGlobalStats();
        }
        if (typeof financeBridge !== "undefined") {
            financeStats = financeBridge.getFinanceMetrics();
        }
    }

    Component.onCompleted: refresh()

    Item {
        width: root.availableWidth
        implicitHeight: mainCol.implicitHeight + (Theme.spacingLG * 2)

        ColumnLayout {
            id: mainCol
            anchors.fill: parent
            anchors.margins: Theme.spacingLG
            spacing: Theme.spacingLG

        // Header Greeting
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingMD

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Text {
                    text: "Good day, CADDESK"
                    color: Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontDisplay
                    font.weight: Theme.weightBold
                }

                Text {
                    text: "Institute Administration & Real-Time Performance Overview"
                    color: Theme.textMuted
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSmall
                }
            }

            RowLayout {
                spacing: Theme.spacingSM

                SecondaryButton {
                    text: "Refresh Stats"
                    iconName: "refresh"
                    onClicked: root.refresh()
                }

                PrimaryButton {
                    text: "New Admission"
                    iconName: "plus"
                    onClicked: crmBridge.navigateTo("Admissions")
                }
            }
        }

        // Top 4 StatCards
        GridLayout {
            Layout.fillWidth: true
            columns: root.width > 1100 ? 4 : (root.width > 700 ? 2 : 1)
            columnSpacing: Theme.spacingMD
            rowSpacing: Theme.spacingMD

            StatCard {
                title: "Total Students"
                value: String(root.globalStats.total_students || 0)
                subtext: `${root.globalStats.active_students || 0} active enrollments`
                iconName: "students"
                iconColor: Theme.primary
                iconBgColor: Theme.primarySoft
                trendText: "+Active"
                isPositiveTrend: true
            }

            StatCard {
                title: "Fees Collected"
                value: "₹" + Number(root.globalStats.total_fees_collected || 0).toLocaleString("en-IN")
                subtext: `Today: ₹${Number(root.financeStats.today_collected || 0).toLocaleString("en-IN")}`
                iconName: "fees"
                iconColor: Theme.accent
                iconBgColor: Theme.accentSoft
                trendText: "Total"
                isPositiveTrend: true
            }

            StatCard {
                title: "Outstanding Dues"
                value: "₹" + Number(root.globalStats.total_pending_dues || 0).toLocaleString("en-IN")
                subtext: `${root.financeStats.overdue_count || 0} overdue installments`
                iconName: "dollar-sign"
                iconColor: Theme.danger
                iconBgColor: Theme.dangerSoft
                trendText: "Due"
                isPositiveTrend: false
            }

            StatCard {
                title: "Active Batches"
                value: String(root.globalStats.active_batches || 0)
                subtext: `${root.globalStats.total_courses || 0} Course Programs`
                iconName: "batches"
                iconColor: Theme.info
                iconBgColor: Theme.infoSoft
                trendText: "Live"
                isPositiveTrend: true
            }
        }

        // Quick Actions Row
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 70
            radius: Theme.radiusLG
            color: Theme.surface
            border.color: Theme.border
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingLG
                anchors.rightMargin: Theme.spacingLG
                spacing: Theme.spacingMD

                Text {
                    text: "Quick Actions:"
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSmall
                    font.weight: Theme.weightBold
                }

                SecondaryButton {
                    text: "View Students"
                    iconName: "students"
                    onClicked: crmBridge.navigateTo("Students")
                }

                SecondaryButton {
                    text: "Fees Ledger"
                    iconName: "fees"
                    onClicked: crmBridge.navigateTo("Fees")
                }

                SecondaryButton {
                    text: "Batch Schedules"
                    iconName: "batches"
                    onClicked: crmBridge.navigateTo("Batches")
                }

                SecondaryButton {
                    text: "Message Automation"
                    iconName: "messaging"
                    onClicked: crmBridge.navigateTo("Communications")
                }

                Item { Layout.fillWidth: true }

                SecondaryButton {
                    text: "Export Roster"
                    iconName: "download"
                    onClicked: reportsBridge.generateStudentRosterReport()
                }
            }
        }

        // Main Dashboard Grid: Split into Attention Required & Institute Overview
        GridLayout {
            Layout.fillWidth: true
            columns: root.width > 950 ? 2 : 1
            columnSpacing: Theme.spacingLG
            rowSpacing: Theme.spacingLG

            // Left Card: Attention & Fee Status
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 340
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "Fee Collection Status"
                            color: Theme.textPrimary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontTitle
                            font.weight: Theme.weightBold
                            Layout.fillWidth: true
                        }

                        SecondaryButton {
                            text: "Manage Dues"
                            customHeight: 30
                            onClicked: crmBridge.navigateTo("Fees")
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: Theme.borderSubtle
                    }

                    // Breakdown Rows
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingMD

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            Text {
                                text: "Fully Paid Students"
                                color: Theme.textSecondary
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSmall
                            }
                            Text {
                                text: String(root.financeStats.paid_students || 0)
                                color: Theme.successText
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontHeader
                                font.weight: Theme.weightBold
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            Text {
                                text: "Partial Balance"
                                color: Theme.textSecondary
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSmall
                            }
                            Text {
                                text: String(root.financeStats.partial_students || 0)
                                color: Theme.warningText
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontHeader
                                font.weight: Theme.weightBold
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            Text {
                                text: "Pending / Overdue"
                                color: Theme.textSecondary
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSmall
                            }
                            Text {
                                text: String(root.financeStats.pending_students || 0)
                                color: Theme.dangerText
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontHeader
                                font.weight: Theme.weightBold
                            }
                        }
                    }

                    // Progress Bar
                    Rectangle {
                        Layout.fillWidth: true
                        height: 12
                        radius: 6
                        color: Theme.surfaceElevated

                        Row {
                            anchors.fill: parent
                            clip: true

                            Rectangle {
                                width: {
                                    var total = root.globalStats.total_students || 1;
                                    var paid = root.financeStats.paid_students || 0;
                                    return (paid / total) * parent.width;
                                }
                                height: parent.height
                                color: Theme.success
                            }

                            Rectangle {
                                width: {
                                    var total = root.globalStats.total_students || 1;
                                    var part = root.financeStats.partial_students || 0;
                                    return (part / total) * parent.width;
                                }
                                height: parent.height
                                color: Theme.warning
                            }

                            Rectangle {
                                width: {
                                    var total = root.globalStats.total_students || 1;
                                    var pend = root.financeStats.pending_students || 0;
                                    return (pend / total) * parent.width;
                                }
                                height: parent.height
                                color: Theme.danger
                            }
                        }
                    }

                    Text {
                        text: "• Use the Message Automation module to dispatch WhatsApp payment reminders to overdue students with 1-click."
                        color: Theme.textMuted
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSmall
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            // Right Card: Recent System Activity
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 340
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: "System Health & Integrity"
                            color: Theme.textPrimary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontTitle
                            font.weight: Theme.weightBold
                            Layout.fillWidth: true
                        }

                        StatusBadge {
                            status: "Active"
                            text: "Database Healthy"
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: Theme.borderSubtle
                    }

                    ActivityTimeline {
                        Layout.fillWidth: true
                        items: [
                            {
                                "title": "SQLite Database Operational",
                                "time": "Live",
                                "description": `Storage Size: ${root.globalStats.db_size_kb || 0} KB · Encrypted Local Session`,
                                "color": Theme.primary
                            },
                            {
                                "title": "Auto-Backup Schedule Ready",
                                "time": "Standard",
                                "description": "Automatic pre-update and manual backup safeguards active.",
                                "color": Theme.info
                            },
                            {
                                "title": "Course Programs Catalog",
                                "time": "Synced",
                                "description": `${root.globalStats.total_courses || 0} standard technical courses loaded and ready for enrollment.`,
                                "color": Theme.accent
                            }
                        ]
                    }
                }
            }
        }
    }
}
}
