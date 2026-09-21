import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: parent.width
    clip: true
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    Connections {
        target: typeof reportsBridge !== "undefined" ? reportsBridge : null
        function onReportGenerated(success, msg, path) {
            if (success) {
                crmBridge.showToast(msg, "success", "Report Generated");
            } else {
                crmBridge.showToast(msg, "error", "Export Failed");
            }
        }
    }

    ColumnLayout {
        width: parent.width
        anchors.leftMargin: Theme.spacingLG
        anchors.rightMargin: Theme.spacingLG
        spacing: Theme.spacingLG
        Layout.topMargin: Theme.spacingLG
        Layout.bottomMargin: Theme.spacingXL

        // Header
        PageHeader {
            title: "Reports & Financial Analytics"
            subtitle: "Generate management summaries, export Excel reports with custom save locations, and generate student PDF dossiers"
        }

        // Report Cards Grid
        GridLayout {
            Layout.fillWidth: true
            columns: root.width > 900 ? 2 : 1
            columnSpacing: Theme.spacingLG
            rowSpacing: Theme.spacingLG

            // Card 1: Complete Student Roster Export
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 230
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    RowLayout {
                        spacing: Theme.spacingMD
                        Rectangle {
                            width: 42
                            height: 42
                            radius: Theme.radiusMD
                            color: Theme.primarySoft
                            Icon { anchors.centerIn: parent; name: "students"; size: 20; color: Theme.primary }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Text { text: "Complete Student Roster Export"; color: Theme.textPrimary; font.pixelSize: Theme.fontTitle; font.weight: Theme.weightBold }
                            Text { text: "Full Excel spreadsheet containing all active and enrolled students, contact info, and course allocations."; color: Theme.textMuted; font.pixelSize: Theme.fontSmall; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSM

                        PrimaryButton {
                            Layout.fillWidth: true
                            text: "💾 Save Master Excel to PC..."
                            iconName: "download"
                            onClicked: reportsBridge.generateStudentRosterWithSaveDialog()
                        }
                    }
                }
            }

            // Card 2: Fee Collections Ledger
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 230
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    RowLayout {
                        spacing: Theme.spacingMD
                        Rectangle {
                            width: 42
                            height: 42
                            radius: Theme.radiusMD
                            color: Theme.accentSoft
                            Icon { anchors.centerIn: parent; name: "fees"; size: 20; color: Theme.accent }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Text { text: "Fee Collections & Installments Ledger"; color: Theme.textPrimary; font.pixelSize: Theme.fontTitle; font.weight: Theme.weightBold }
                            Text { text: "Detailed audit log of every recorded installment, payment mode breakdown, and official receipt numbers."; color: Theme.textMuted; font.pixelSize: Theme.fontSmall; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSM

                        PrimaryButton {
                            Layout.fillWidth: true
                            text: "💾 Save Fee Ledger Excel..."
                            iconName: "download"
                            onClicked: reportsBridge.generateFeeLedgerWithSaveDialog()
                        }

                        SecondaryButton {
                            text: "View Ledger"
                            iconName: "fees"
                            onClicked: crmBridge.navigateTo("Fees")
                        }
                    }
                }
            }

            // Card 3: Outstanding Dues & Overdue Summary
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 230
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    RowLayout {
                        spacing: Theme.spacingMD
                        Rectangle {
                            width: 42
                            height: 42
                            radius: Theme.radiusMD
                            color: Theme.dangerSoft
                            Icon { anchors.centerIn: parent; name: "dollar-sign"; size: 20; color: Theme.danger }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Text { text: "Outstanding Dues Recovery Report"; color: Theme.textPrimary; font.pixelSize: Theme.fontTitle; font.weight: Theme.weightBold }
                            Text { text: "List of all students with pending fee installments, days elapsed since last payment, and direct contact details."; color: Theme.textMuted; font.pixelSize: Theme.fontSmall; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSM

                        PrimaryButton {
                            Layout.fillWidth: true
                            text: "💾 Save Overdue Defaulters Excel..."
                            iconName: "download"
                            onClicked: reportsBridge.generateOverdueReportWithSaveDialog()
                        }

                        SecondaryButton {
                            text: "WhatsApp Queue"
                            iconName: "messaging"
                            onClicked: crmBridge.navigateTo("Communications")
                        }
                    }
                }
            }

            // Card 4: Student PDF Documents & Admission Slips
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 230
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    RowLayout {
                        spacing: Theme.spacingMD
                        Rectangle {
                            width: 42
                            height: 42
                            radius: Theme.radiusMD
                            color: Theme.infoSoft
                            Icon { anchors.centerIn: parent; name: "documents"; size: 20; color: Theme.info }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Text { text: "Student PDF Documents & Slips"; color: Theme.textPrimary; font.pixelSize: Theme.fontTitle; font.weight: Theme.weightBold }
                            Text { text: "Generate, save to PC, and print official PDF admission forms, fee payment receipts, and enrollment slips for any student."; color: Theme.textMuted; font.pixelSize: Theme.fontSmall; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    RowLayout {
                        Layout.fillWidth: true

                        PrimaryButton {
                            Layout.fillWidth: true
                            text: "📄 Open Student PDF Generator"
                            iconName: "documents"
                            onClicked: crmBridge.navigateTo("Documents")
                        }
                    }
                }
            }
        }
    }
}
