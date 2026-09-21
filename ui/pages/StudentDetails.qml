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

    property string studentId: ""
    property var studentData: ({})
    property string activeTab: "Overview"

    function loadStudent(id) {
        if (!id || String(id).trim() === "" || String(id) === "0") return;
        root.studentId = String(id);
        if (typeof studentsBridge !== "undefined") {
            root.studentData = studentsBridge.getStudentById(String(id));
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

            // Top Navigation & Actions Bar
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingSM

                SecondaryButton {
                    text: "Back to Students"
                    iconName: "chevron-left"
                    customHeight: 36
                    onClicked: crmBridge.navigateTo("Students")
                }

                Item { Layout.fillWidth: true }

                PrimaryButton {
                    text: "Edit Details"
                    iconName: "edit"
                    customHeight: 36
                    onClicked: {
                        if (typeof admissionsPage !== "undefined") {
                            admissionsPage.loadStudentForEdit(root.studentId);
                        }
                        crmBridge.navigateTo("Admissions");
                    }
                }

                SecondaryButton {
                    text: "Physical Form"
                    iconName: "document"
                    customHeight: 36
                    onClicked: {
                        root.activeTab = "Physical Admission Form";
                    }
                }

                SecondaryButton {
                    text: "Print Slip"
                    iconName: "download"
                    customHeight: 36
                    onClicked: {
                        var pdf = studentsBridge.generateAdmissionPdf(root.studentId);
                        if (pdf) {
                            crmBridge.showToast("Generated Admission Slip PDF", "success", "PDF Ready");
                            reportsBridge.openDocument(pdf);
                        }
                    }
                }

                SecondaryButton {
                    text: "Send WhatsApp"
                    iconName: "whatsapp"
                    customHeight: 36
                    onClicked: {
                        if (typeof communicationsPage !== "undefined") {
                            communicationsPage.selectStudentForMessaging(root.studentData);
                        }
                        crmBridge.navigateTo("Communications");
                    }
                }
            }

            // Student Banner Card (Balanced & Gap-Free Design)
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 120
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingLG

                    // Student Avatar
                    Avatar {
                        name: root.studentData.name || ""
                        photoUrl: root.studentData.photo_url || ""
                        size: 72
                    }

                    // Student Identity Details
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        RowLayout {
                            spacing: Theme.spacingSM

                            Text {
                                text: root.studentData.name || "Student Profile"
                                color: Theme.textPrimary
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontHeader
                                font.weight: Theme.weightBold
                            }

                            Rectangle {
                                height: 22
                                radius: Theme.radiusSM
                                color: Theme.surfaceElevated
                                border.color: Theme.border
                                border.width: 1
                                implicitWidth: idLabel.implicitWidth + 12

                                Text {
                                    id: idLabel
                                    anchors.centerIn: parent
                                    text: root.studentData.id_no || ""
                                    color: Theme.textSecondary
                                    font.family: Theme.fontMono
                                    font.pixelSize: Theme.fontCaption
                                    font.weight: Theme.weightBold
                                }
                            }

                            StatusDropdown {
                                currentStatus: root.studentData.status || "Active"
                                onStatusSelected: newStatus => {
                                    var res = studentsBridge.updateStudentStatus(root.studentId, newStatus);
                                    if (res) {
                                        crmBridge.showToast(`Updated status to "${newStatus}"`, "success", "Status Updated");
                                        root.loadStudent(root.studentId);
                                    } else {
                                        crmBridge.showToast("Failed to update status", "error", "Update Error");
                                    }
                                }
                            }

                            StatusBadge {
                                status: root.studentData.fee_status || "Pending"
                            }

                            Rectangle {
                                visible: root.studentData.has_admission_form === true
                                height: 22
                                radius: Theme.radiusSM
                                color: Theme.infoSoft
                                border.color: Theme.info
                                border.width: 1
                                implicitWidth: formBadge.implicitWidth + 12

                                Text {
                                    id: formBadge
                                    anchors.centerIn: parent
                                    text: "📄 Form Scanned"
                                    color: Theme.info
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.weightBold
                                }
                            }
                        }

                        Text {
                            text: `${root.studentData.course_name || "No Course"}  ·  Batch: ${root.studentData.primary_batch || "Unassigned"}  ·  Enrolled: ${root.studentData.admission_date || "N/A"}  ·  Last Fee Paid: ${root.studentData.last_paid_date_str || "—"} (${root.studentData.days_ago_str || "No payment yet"})`
                            color: Theme.textSecondary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSmall
                        }
                    }

                    // Balanced Financial Summary Cluster
                    RowLayout {
                        spacing: Theme.spacingMD

                        // Net Payable
                        Rectangle {
                            height: 72
                            implicitWidth: 140
                            radius: Theme.radiusMD
                            color: Theme.surfaceElevated
                            border.color: Theme.borderSubtle
                            border.width: 1

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 2

                                Text {
                                    text: "Net Payable Fee"
                                    color: Theme.textSecondary
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.weightMedium
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Text {
                                    text: "₹" + Number(root.studentData.net_payable_fee || 0).toLocaleString("en-IN")
                                    color: Theme.textPrimary
                                    font.family: Theme.fontMono
                                    font.pixelSize: Theme.fontTitle
                                    font.weight: Theme.weightBold
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }

                        // Total Paid
                        Rectangle {
                            height: 72
                            implicitWidth: 140
                            radius: Theme.radiusMD
                            color: Theme.surfaceElevated
                            border.color: Theme.borderSubtle
                            border.width: 1

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 2

                                Text {
                                    text: "Total Paid"
                                    color: Theme.textSecondary
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.weightMedium
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Text {
                                    text: "₹" + Number(root.studentData.total_paid_fee || 0).toLocaleString("en-IN")
                                    color: root.studentData.total_paid_fee > 0 ? Theme.successText : Theme.textMuted
                                    font.family: Theme.fontMono
                                    font.pixelSize: Theme.fontTitle
                                    font.weight: Theme.weightBold
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }

                        // Outstanding Balance
                        Rectangle {
                            height: 72
                            implicitWidth: 160
                            radius: Theme.radiusMD
                            color: root.studentData.balance_due > 0 ? Theme.dangerSoft : Theme.successSoft
                            border.color: root.studentData.balance_due > 0 ? Theme.danger : Theme.success
                            border.width: 1

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 2

                                Text {
                                    text: root.studentData.balance_due > 0 ? "Outstanding Balance" : "Fees Settled"
                                    color: root.studentData.balance_due > 0 ? Theme.dangerText : Theme.successText
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.weightBold
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Text {
                                    text: "₹" + Number(root.studentData.balance_due || 0).toLocaleString("en-IN")
                                    color: root.studentData.balance_due > 0 ? Theme.dangerText : Theme.successText
                                    font.family: Theme.fontMono
                                    font.pixelSize: Theme.fontTitle
                                    font.weight: Theme.weightBold
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                    }
                }
            }

            // Segmented Tabs
            FilterBar {
                options: ["Overview", "Fee Installments", "Academic & Sessions", "Physical Admission Form"]
                selectedOption: root.activeTab
                onSelectionChanged: opt => root.activeTab = opt
            }

            // Tab 1: Overview & Contact Information
            Rectangle {
                visible: root.activeTab === "Overview"
                Layout.fillWidth: true
                implicitHeight: overviewLayout.implicitHeight + (Theme.spacingLG * 2)
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    id: overviewLayout
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingLG

                    FormSection {
                        title: "Personal & Contact Details"
                        description: "Student identity, phone numbers, and emergency contact details"

                        GridLayout {
                            columns: 3
                            columnSpacing: Theme.spacingLG
                            rowSpacing: Theme.spacingMD
                            Layout.fillWidth: true

                            FormField { label: "Full Name"; text: root.studentData.name || ""; readOnly: true }
                            FormField { label: "Mobile Number"; text: root.studentData.mobile_no || ""; readOnly: true }
                            FormField { label: "Email Address"; text: root.studentData.email || "N/A"; readOnly: true }

                            FormField { label: "Father's Name"; text: root.studentData.father_name || "N/A"; readOnly: true }
                            FormField { label: "Father Contact"; text: root.studentData.father_contact || "N/A"; readOnly: true }
                            FormField { label: "Mother's Name"; text: root.studentData.mother_name || "N/A"; readOnly: true }

                            FormField { label: "Date of Birth"; text: root.studentData.dob || "N/A"; readOnly: true }
                            FormField { label: "Aadhar Number"; text: root.studentData.aadhar_no || "N/A"; readOnly: true }
                            FormField { label: "Alternate Phone"; text: root.studentData.alternate_contact || "N/A"; readOnly: true }
                        }
                    }

                    FormSection {
                        title: "Academic & College Background"

                        GridLayout {
                            columns: 3
                            columnSpacing: Theme.spacingLG
                            rowSpacing: Theme.spacingMD
                            Layout.fillWidth: true

                            FormField { label: "College / School"; text: root.studentData.college_school || "N/A"; readOnly: true }
                            FormField { label: "Year / Semester"; text: root.studentData.year_semester || "N/A"; readOnly: true }
                            FormField { label: "Assigned Faculty Mentor"; text: root.studentData.assigned_staff_name || "Unassigned"; readOnly: true }
                        }
                    }

                    FormSection {
                        title: "Address & Location"

                        GridLayout {
                            columns: 3
                            columnSpacing: Theme.spacingLG
                            rowSpacing: Theme.spacingMD
                            Layout.fillWidth: true

                            FormField { label: "Permanent Address"; text: root.studentData.permanent_address || "N/A"; readOnly: true; Layout.columnSpan: 2 }
                            FormField { label: "District"; text: root.studentData.district || "N/A"; readOnly: true }
                            FormField { label: "State"; text: root.studentData.state || "Rajasthan"; readOnly: true }
                            FormField { label: "PIN Code"; text: root.studentData.pin_code || "N/A"; readOnly: true }
                        }
                    }
                }
            }

            // Tab 2: Fee Installments & Receipts Ledger
            Rectangle {
                visible: root.activeTab === "Fee Installments"
                Layout.fillWidth: true
                implicitHeight: feesLayout.implicitHeight + (Theme.spacingLG * 2)
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    id: feesLayout
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    // Fee Summary Cards
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingMD

                        StatCard {
                            title: "Course Fee"
                            value: "₹" + Number(root.studentData.total_course_fee || 0).toLocaleString("en-IN")
                            iconName: "fees"
                        }

                        StatCard {
                            title: "Scholarship Discount"
                            value: "₹" + Number(root.studentData.scholarship_discount || 0).toLocaleString("en-IN")
                            iconName: "dollar-sign"
                        }

                        StatCard {
                            title: "Net Payable"
                            value: "₹" + Number(root.studentData.net_payable_fee || 0).toLocaleString("en-IN")
                            iconName: "fees"
                            iconColor: Theme.accent
                        }

                        StatCard {
                            title: "Total Paid"
                            value: "₹" + Number(root.studentData.total_paid_fee || 0).toLocaleString("en-IN")
                            iconName: "check"
                            iconColor: Theme.success
                        }
                    }

                    Text {
                        text: "Installment Schedule & Receipts"
                        color: Theme.textPrimary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontTitle
                        font.weight: Theme.weightBold
                        Layout.topMargin: Theme.spacingMD
                    }

                    DataTable {
                        Layout.fillWidth: true
                        implicitHeight: 280
                        model: root.studentData.installments || []
                        showPagination: false

                        columns: [
                            { "title": "#", "role": "installment_no", "width": 50, "isPrimary": true },
                            { "title": "Due Date", "role": "due_date", "width": 110 },
                            { "title": "Due Amount", "role": "due_amount", "width": 120, "isCurrency": true, "alignRight": true },
                            { "title": "Paid Amount", "role": "paid_amount", "width": 120, "isCurrency": true, "alignRight": true },
                            { "title": "Paid Date", "role": "payment_date", "width": 110 },
                            { "title": "Payment Mode", "role": "payment_mode", "width": 110 },
                            { "title": "Receipt No", "role": "receipt_no", "width": 120, "isHighlight": true },
                            { "title": "Status", "role": "status", "width": 100, "isBadge": true },
                            { "title": "Print Receipt", "role": "actions", "width": 100, "isAction": true, "actions": ["download"], "alignRight": true }
                        ]

                        onRowAction: (action, rowData, index) => {
                            if (action === "download") {
                                var pdf = studentsBridge.generateReceiptPdf(root.studentId, rowData.id);
                                if (pdf) {
                                    crmBridge.showToast(`Receipt PDF created for installment #${rowData.installment_no}`, "success", "Receipt Ready");
                                    reportsBridge.openDocument(pdf);
                                }
                            }
                        }
                    }
                }
            }

            // Tab 3: Academic & Course Sessions
            Rectangle {
                visible: root.activeTab === "Academic & Sessions"
                Layout.fillWidth: true
                implicitHeight: sessionsLayout.implicitHeight + (Theme.spacingLG * 2)
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                ColumnLayout {
                    id: sessionsLayout
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLG
                    spacing: Theme.spacingMD

                    Text {
                        text: "Course Modules & Study Material Log"
                        color: Theme.textPrimary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontTitle
                        font.weight: Theme.weightBold
                    }

                    DataTable {
                        Layout.fillWidth: true
                        implicitHeight: 280
                        model: root.studentData.course_sessions || []
                        showPagination: false

                        columns: [
                            { "title": "Session #", "role": "session_no", "width": 90, "isPrimary": true },
                            { "title": "Module / Session Title", "role": "session_name", "width": 200, "fill": true },
                            { "title": "Faculty", "role": "faculty_name", "width": 160 },
                            { "title": "Book Issued", "role": "book_issued", "width": 110 },
                            { "title": "Issue Date", "role": "book_issue_date", "width": 110 },
                            { "title": "Book Title", "role": "book_title", "width": 180 }
                        ]
                    }
                }
            }

            // Tab 4: Scanned Physical Admission Form Viewer
            Rectangle {
                visible: root.activeTab === "Physical Admission Form"
                Layout.fillWidth: true
                implicitHeight: 680
                radius: Theme.radiusLG
                color: Theme.surface
                border.color: Theme.border
                border.width: 1

                FormImageViewer {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingMD
                    imageUrl: root.studentData.admission_form_url || ""
                    rawFilePath: root.studentData.admission_form_raw_path || ""
                    studentId: root.studentId
                    studentName: root.studentData.name || ""
                    studentIdNo: root.studentData.id_no || ""
                }
            }
        }
    }
}
