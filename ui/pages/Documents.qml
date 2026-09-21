import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property var studentsList: []
    property var filteredStudents: []
    property var selectedStudent: null
    property string searchQuery: ""
    property string selectedDocType: "admission" // "admission", "fee_receipt", "profile"

    function refresh() {
        if (typeof reportsBridge !== "undefined") {
            studentsList = reportsBridge.getStudentsList();
            applyFilter();
        }
    }

    function applyFilter() {
        var res = studentsList;
        if (searchQuery.trim() !== "") {
            var q = searchQuery.toLowerCase();
            res = res.filter(s =>
                s.name.toLowerCase().includes(q) ||
                s.course_name.toLowerCase().includes(q) ||
                s.mobile_no.includes(q) ||
                s.id_no.toLowerCase().includes(q)
            );
        }
        filteredStudents = res;
        if (filteredStudents.length > 0 && (!selectedStudent || !selectedStudent.id)) {
            selectedStudent = filteredStudents[0];
        }
    }

    Component.onCompleted: refresh()

    Connections {
        target: typeof reportsBridge !== "undefined" ? reportsBridge : null
        function onReportGenerated(success, msg, path) {
            if (success) {
                crmBridge.showToast(msg, "success", "PDF Generated");
            } else {
                crmBridge.showToast(msg, "error", "PDF Generation Failed");
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingMD

        // Page Header
        PageHeader {
            title: "Student PDF Documents & Certificates"
            subtitle: "Generate, save, and print official PDF admission forms, fee payment receipts, and student summaries"
            countText: `${root.studentsList.length} enrolled students`

            SecondaryButton {
                text: "Refresh Data"
                iconName: "refresh"
                onClicked: root.refresh()
            }
        }

        // Main Studio Layout
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingMD

            // 1. Left Panel: Student Selector
            Rectangle {
                Layout.preferredWidth: 320
                Layout.minimumWidth: 280
                Layout.fillHeight: true
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingMD
                    spacing: Theme.spacingSM

                    Text {
                        text: "Select Student"
                        color: Theme.textPrimary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontBody
                        font.weight: Theme.weightBold
                    }

                    SearchBar {
                        placeholderText: "Search name, course, mobile..."
                        implicitWidth: parent.width
                        onSearchChanged: query => {
                            root.searchQuery = query;
                            root.applyFilter();
                        }
                    }

                    ListView {
                        id: studentListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: root.filteredStudents
                        spacing: 6

                        delegate: Rectangle {
                            id: studentCard
                            readonly property bool isSelected: root.selectedStudent && root.selectedStudent.id === modelData.id
                            width: ListView.view ? ListView.view.width : 280
                            height: 56
                            radius: Theme.radiusMD
                            color: isSelected ? Theme.primarySoft :
                                   (studentMouse.containsMouse ? Theme.surfaceHover : Theme.surfaceElevated)
                            border.color: isSelected ? Theme.primary : Theme.borderSubtle
                            border.width: 1

                            Behavior on color { ColorAnimation { duration: Theme.animFast } }

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 10

                                // Avatar initials
                                Rectangle {
                                    width: 36
                                    height: 36
                                    radius: 18
                                    color: isSelected ? Theme.primary : Theme.surfaceActive

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.name ? modelData.name.charAt(0).toUpperCase() : "S"
                                        color: isSelected ? "#FFFFFF" : Theme.primaryText
                                        font.family: Theme.fontFamily
                                        font.pixelSize: 13
                                        font.weight: Theme.weightBold
                                    }
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 2

                                    Text {
                                        text: modelData.name
                                        color: isSelected ? Theme.primaryText : Theme.textPrimary
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSmall
                                        font.weight: Theme.weightBold
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 6

                                        Text {
                                            text: modelData.course_name || "General"
                                            color: Theme.textMuted
                                            font.family: Theme.fontFamily
                                            font.pixelSize: 11
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }

                                        Text {
                                            text: modelData.balance_due > 0 ? `Due: ₹${Number(modelData.balance_due).toLocaleString('en-IN')}` : "Paid"
                                            color: modelData.balance_due > 0 ? Theme.dangerText : Theme.successText
                                            font.family: Theme.fontFamily
                                            font.pixelSize: 10
                                            font.weight: Theme.weightBold
                                        }
                                    }
                                }
                            }

                            MouseArea {
                                id: studentMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.selectedStudent = modelData
                            }
                        }
                    }
                }
            }

            // 2. Right Panel: PDF Document Options & Generation Workspace
            Rectangle {
                id: rightPanelBox
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ScrollView {
                    id: docScrollView
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    clip: true
                    contentWidth: availableWidth
                    ScrollBar.vertical.policy: ScrollBar.AsNeeded

                    ColumnLayout {
                        width: docScrollView.availableWidth > 0 ? docScrollView.availableWidth : (rightPanelBox.width - 48)
                        spacing: Theme.spacingLG

                        // Selected Student Profile Overview Banner
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 84
                            radius: Theme.radiusMD
                            color: Theme.surfaceElevated
                            border.color: Theme.borderSubtle
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: Theme.spacingMD
                                spacing: Theme.spacingMD

                                Rectangle {
                                    width: 48
                                    height: 48
                                    radius: 24
                                    color: Theme.primarySoft
                                    border.color: Theme.primary
                                    border.width: 1.5

                                    Text {
                                        anchors.centerIn: parent
                                        text: root.selectedStudent && root.selectedStudent.name ? root.selectedStudent.name.charAt(0).toUpperCase() : "S"
                                        color: Theme.primary
                                        font.family: Theme.fontFamily
                                        font.pixelSize: 18
                                        font.weight: Theme.weightBold
                                    }
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 4

                                    RowLayout {
                                        spacing: 8
                                        Text {
                                            text: root.selectedStudent ? root.selectedStudent.name : "Select a student from left panel"
                                            color: Theme.textPrimary
                                            font.family: Theme.fontFamily
                                            font.pixelSize: Theme.fontTitle
                                            font.weight: Theme.weightBold
                                        }

                                        StatusBadge {
                                            status: root.selectedStudent ? root.selectedStudent.status : "Active"
                                        }
                                    }

                                    RowLayout {
                                        spacing: 16
                                        Text {
                                            text: `🎓 Course: <b>${root.selectedStudent ? root.selectedStudent.course_name : '—'}</b>`
                                            color: Theme.textSecondary
                                            font.pixelSize: Theme.fontSmall
                                        }
                                        Text {
                                            text: `📞 Phone: <b>${root.selectedStudent ? root.selectedStudent.mobile_no : '—'}</b>`
                                            color: Theme.textSecondary
                                            font.pixelSize: Theme.fontSmall
                                        }
                                        Text {
                                            text: `💰 Total Fee: <b>₹${root.selectedStudent ? Number(root.selectedStudent.total_fee).toLocaleString('en-IN') : '0'}</b>`
                                            color: Theme.textSecondary
                                            font.pixelSize: Theme.fontSmall
                                        }
                                        Text {
                                            text: `💳 Balance Due: <font color='${root.selectedStudent && root.selectedStudent.balance_due > 0 ? Theme.dangerText : Theme.successText}'><b>₹${root.selectedStudent ? Number(root.selectedStudent.balance_due).toLocaleString('en-IN') : '0'}</b></font>`
                                            color: Theme.textSecondary
                                            font.pixelSize: Theme.fontSmall
                                        }
                                    }
                                }
                            }
                        }

                        // Section Title
                        Text {
                            text: "Select Document Format"
                            color: Theme.textPrimary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontBody
                            font.weight: Theme.weightBold
                        }

                        // Document Option Tiles (Vertical Full-Width Cards for Maximum Clarity & Cleanliness)
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingMD

                            // Option 1: Official Admission Slip
                            Rectangle {
                                Layout.fillWidth: true
                                implicitHeight: 88
                                radius: Theme.radiusMD
                                color: root.selectedDocType === "admission" ? Theme.primarySoft : Theme.surfaceElevated
                                border.color: root.selectedDocType === "admission" ? Theme.primary : Theme.borderSubtle
                                border.width: root.selectedDocType === "admission" ? 2 : 1

                                Behavior on color { ColorAnimation { duration: Theme.animFast } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: Theme.spacingMD
                                    spacing: Theme.spacingMD

                                    Rectangle {
                                        width: 44
                                        height: 44
                                        radius: Theme.radiusMD
                                        color: root.selectedDocType === "admission" ? Theme.primary : Theme.surfaceActive

                                        Text {
                                            anchors.centerIn: parent
                                            text: "📄"
                                            font.pixelSize: 20
                                        }
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 3

                                        RowLayout {
                                            spacing: 8
                                            Text {
                                                text: "Official Admission & Registration Slip"
                                                color: root.selectedDocType === "admission" ? Theme.primaryText : Theme.textPrimary
                                                font.pixelSize: Theme.fontBody
                                                font.weight: Theme.weightBold
                                            }
                                            Rectangle {
                                                width: 80
                                                height: 20
                                                radius: 10
                                                color: Theme.primarySoft
                                                Text {
                                                    anchors.centerIn: parent
                                                    text: "Official Form"
                                                    color: Theme.primary
                                                    font.pixelSize: 10
                                                    font.weight: Theme.weightBold
                                                }
                                            }
                                        }

                                        Text {
                                            text: "Complete CADDESK registration slip with passport photo placeholder, parent contact info, address, enrolled course, fee installment schedule, rules & declaration, and signature stamp blocks."
                                            color: Theme.textMuted
                                            font.pixelSize: 11
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }

                                    // Selection Radio Indicator
                                    Rectangle {
                                        width: 22
                                        height: 22
                                        radius: 11
                                        border.color: root.selectedDocType === "admission" ? Theme.primary : Theme.border
                                        border.width: 2
                                        color: "transparent"

                                        Rectangle {
                                            anchors.centerIn: parent
                                            width: 12
                                            height: 12
                                            radius: 6
                                            color: Theme.primary
                                            visible: root.selectedDocType === "admission"
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.selectedDocType = "admission"
                                }
                            }

                            // Option 2: Fee Payment Receipt
                            Rectangle {
                                Layout.fillWidth: true
                                implicitHeight: 88
                                radius: Theme.radiusMD
                                color: root.selectedDocType === "fee_receipt" ? Theme.accentSoft : Theme.surfaceElevated
                                border.color: root.selectedDocType === "fee_receipt" ? Theme.accent : Theme.borderSubtle
                                border.width: root.selectedDocType === "fee_receipt" ? 2 : 1

                                Behavior on color { ColorAnimation { duration: Theme.animFast } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: Theme.spacingMD
                                    spacing: Theme.spacingMD

                                    Rectangle {
                                        width: 44
                                        height: 44
                                        radius: Theme.radiusMD
                                        color: root.selectedDocType === "fee_receipt" ? Theme.accent : Theme.surfaceActive

                                        Text {
                                            anchors.centerIn: parent
                                            text: "🧾"
                                            font.pixelSize: 20
                                        }
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 3

                                        RowLayout {
                                            spacing: 8
                                            Text {
                                                text: "Fee Payment Receipt & Account Statement"
                                                color: root.selectedDocType === "fee_receipt" ? Theme.accentHover : Theme.textPrimary
                                                font.pixelSize: Theme.fontBody
                                                font.weight: Theme.weightBold
                                            }
                                            Rectangle {
                                                width: 70
                                                height: 20
                                                radius: 10
                                                color: Theme.accentSoft
                                                Text {
                                                    anchors.centerIn: parent
                                                    text: "Receipt"
                                                    color: Theme.accent
                                                    font.pixelSize: 10
                                                    font.weight: Theme.weightBold
                                                }
                                            }
                                        }

                                        Text {
                                            text: "Official payment receipt voucher showing total course fee, discounts, breakdown of recorded installment payments, transaction IDs, payment modes, and remaining balance."
                                            color: Theme.textMuted
                                            font.pixelSize: 11
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }

                                    // Selection Radio Indicator
                                    Rectangle {
                                        width: 22
                                        height: 22
                                        radius: 11
                                        border.color: root.selectedDocType === "fee_receipt" ? Theme.accent : Theme.border
                                        border.width: 2
                                        color: "transparent"

                                        Rectangle {
                                            anchors.centerIn: parent
                                            width: 12
                                            height: 12
                                            radius: 6
                                            color: Theme.accent
                                            visible: root.selectedDocType === "fee_receipt"
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.selectedDocType = "fee_receipt"
                                }
                            }

                            // Option 3: Full Student Profile Summary
                            Rectangle {
                                Layout.fillWidth: true
                                implicitHeight: 88
                                radius: Theme.radiusMD
                                color: root.selectedDocType === "profile" ? Theme.infoSoft : Theme.surfaceElevated
                                border.color: root.selectedDocType === "profile" ? Theme.info : Theme.borderSubtle
                                border.width: root.selectedDocType === "profile" ? 2 : 1

                                Behavior on color { ColorAnimation { duration: Theme.animFast } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: Theme.spacingMD
                                    spacing: Theme.spacingMD

                                    Rectangle {
                                        width: 44
                                        height: 44
                                        radius: Theme.radiusMD
                                        color: root.selectedDocType === "profile" ? Theme.info : Theme.surfaceActive

                                        Text {
                                            anchors.centerIn: parent
                                            text: "🎓"
                                            font.pixelSize: 20
                                        }
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 3

                                        RowLayout {
                                            spacing: 8
                                            Text {
                                                text: "Student Profile & Enrollment Dossier"
                                                color: root.selectedDocType === "profile" ? Theme.infoText : Theme.textPrimary
                                                font.pixelSize: Theme.fontBody
                                                font.weight: Theme.weightBold
                                            }
                                            Rectangle {
                                                width: 60
                                                height: 20
                                                radius: 10
                                                color: Theme.infoSoft
                                                Text {
                                                    anchors.centerIn: parent
                                                    text: "Dossier"
                                                    color: Theme.info
                                                    font.pixelSize: 10
                                                    font.weight: Theme.weightBold
                                                }
                                            }
                                        }

                                        Text {
                                            text: "Comprehensive academic and administrative profile including enrollment date, batch timing, mentor details, and verified fee schedule."
                                            color: Theme.textMuted
                                            font.pixelSize: 11
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }

                                    // Selection Radio Indicator
                                    Rectangle {
                                        width: 22
                                        height: 22
                                        radius: 11
                                        border.color: root.selectedDocType === "profile" ? Theme.info : Theme.border
                                        border.width: 2
                                        color: "transparent"

                                        Rectangle {
                                            anchors.centerIn: parent
                                            width: 12
                                            height: 12
                                            radius: 6
                                            color: Theme.info
                                            visible: root.selectedDocType === "profile"
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.selectedDocType = "profile"
                                }
                            }
                        }

                        // Generation Action Bar
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: 110
                            radius: Theme.radiusMD
                            color: Theme.surfaceElevated
                            border.color: Theme.borderSubtle
                            border.width: 1

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: Theme.spacingMD
                                spacing: Theme.spacingSM

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: Theme.spacingMD

                                    PrimaryButton {
                                        Layout.fillWidth: true
                                        text: "Save PDF to Computer..."
                                        iconName: "download"
                                        customHeight: 46
                                        onClicked: {
                                            if (!root.selectedStudent || !root.selectedStudent.id) {
                                                crmBridge.showToast("Please select a student first.", "warning", "No Student Selected");
                                                return;
                                            }
                                            reportsBridge.generateStudentPdfWithSaveDialog(root.selectedStudent.id, root.selectedDocType);
                                        }
                                    }

                                    SecondaryButton {
                                        Layout.preferredWidth: 200
                                        text: "Preview / Print PDF"
                                        iconName: "documents"
                                        customHeight: 46
                                        onClicked: {
                                            if (!root.selectedStudent || !root.selectedStudent.id) {
                                                crmBridge.showToast("Please select a student first.", "warning", "No Student Selected");
                                                return;
                                            }
                                            reportsBridge.previewStudentPdf(root.selectedStudent.id, root.selectedDocType);
                                        }
                                    }
                                }

                                Text {
                                    text: "💡 <b>Save PDF to Computer</b> will open your Windows save window so you can choose any folder on your PC (Desktop, Documents, etc.)"
                                    color: Theme.textMuted
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 11
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
