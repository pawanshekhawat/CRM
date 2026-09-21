import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property var financeMetrics: ({})
    property var transactionsList: []
    property var outstandingList: []
    property string activeSubView: "Payments Ledger"
    property string searchQuery: ""

    property var selectedStudentForPayment: null

    function refresh() {
        if (typeof financeBridge !== "undefined") {
            financeMetrics = financeBridge.getFinanceMetrics();
            transactionsList = financeBridge.getTransactions(searchQuery, "All");
            outstandingList = financeBridge.getOutstandingList(searchQuery, "All");
        }
    }

    Component.onCompleted: refresh()

    function openStudentFeeDetails(studentId) {
        if (!studentId) return;
        if (typeof studentDetailsPage !== "undefined") {
            studentDetailsPage.loadStudent(String(studentId));
            studentDetailsPage.activeTab = "Fee Installments";
        }
        crmBridge.navigateTo("StudentDetails");
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingMD

        // Header
        PageHeader {
            title: "Fees & Finance Workspace"
            subtitle: "Track fee collections, daily receipts, overdue balances, and installments"

            SecondaryButton {
                text: "Refresh Ledger"
                iconName: "refresh"
                onClicked: root.refresh()
            }
        }

        // Metrics Summary
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingMD

            StatCard {
                title: "Total Collection"
                value: "₹" + Number(root.financeMetrics.total_collected || 0).toLocaleString("en-IN")
                subtext: `Total Net: ₹${Number(root.financeMetrics.net_fees_total || 0).toLocaleString("en-IN")}`
                iconName: "fees"
                iconColor: Theme.primary
            }

            StatCard {
                title: "Today's Collection"
                value: "₹" + Number(root.financeMetrics.today_collected || 0).toLocaleString("en-IN")
                subtext: "Settled today"
                iconName: "check"
                iconColor: Theme.accent
            }

            StatCard {
                title: "Total Outstanding"
                value: "₹" + Number(root.financeMetrics.total_outstanding || 0).toLocaleString("en-IN")
                subtext: `${root.financeMetrics.overdue_count || 0} overdue accounts`
                iconName: "dollar-sign"
                iconColor: Theme.danger
            }

            StatCard {
                title: "Enrolled Students"
                value: String(root.financeMetrics.total_students || 0)
                subtext: `${root.financeMetrics.paid_students || 0} fully paid`
                iconName: "students"
                iconColor: Theme.info
            }
        }

        // View Tabs & Search Bar
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 60
            radius: Theme.radiusMD
            color: Theme.surface
            border.color: Theme.border
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingMD
                anchors.rightMargin: Theme.spacingMD
                spacing: Theme.spacingMD

                FilterBar {
                    options: ["Payments Ledger", "Outstanding Dues"]
                    selectedOption: root.activeSubView
                    onSelectionChanged: opt => root.activeSubView = opt
                }

                Item { Layout.fillWidth: true }

                SearchBar {
                    placeholderText: "Search receipts, student name, or ID..."
                    implicitWidth: 320
                    onSearchChanged: query => {
                        root.searchQuery = query;
                        root.refresh();
                    }
                }
            }
        }

        // Subview 1: Payments Ledger
        DataTable {
            visible: root.activeSubView === "Payments Ledger"
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: root.transactionsList
            pageSize: 20

            columns: [
                { "title": "Receipt #", "role": "receipt_no", "width": 120, "isPrimary": true },
                { "title": "Date", "role": "payment_date", "width": 110 },
                { "title": "Student Name", "role": "student_name", "width": 180, "fill": true, "isHighlight": true },
                { "title": "Student ID", "role": "student_id_no", "width": 110, "isMuted": true },
                { "title": "Course", "role": "course_name", "width": 160 },
                { "title": "Amount Paid", "role": "paid_amount", "width": 120, "isCurrency": true, "alignRight": true },
                { "title": "Mode", "role": "payment_mode", "width": 100 },
                { "title": "Print Receipt", "role": "actions", "width": 90, "isAction": true, "actions": ["download"], "alignRight": true }
            ]

            onRowDoubleClicked: (rowData, index) => {
                root.openStudentFeeDetails(rowData.student_id);
            }

            onRowAction: (action, rowData, index) => {
                if (action === "download") {
                    var pdf = studentsBridge.generateReceiptPdf(rowData.student_id, rowData.installment_id);
                    if (pdf) {
                        crmBridge.showToast(`Receipt PDF generated: ${rowData.receipt_no}`, "success", "Receipt Ready");
                        reportsBridge.openDocument(pdf);
                    }
                }
            }
        }

        // Subview 2: Outstanding Balances
        DataTable {
            visible: root.activeSubView === "Outstanding Dues"
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: root.outstandingList
            pageSize: 20

            columns: [
                { "title": "ID", "role": "id_no", "width": 110, "isPrimary": true },
                { "title": "Student Name", "role": "name", "width": 180, "fill": true, "isHighlight": true },
                { "title": "Course Program", "role": "course_name", "width": 160 },
                { "title": "Mobile Number", "role": "mobile_no", "width": 120 },
                { "title": "Total Fee", "role": "total_fee", "width": 110, "isCurrency": true, "alignRight": true },
                { "title": "Paid So Far", "role": "total_paid", "width": 110, "isCurrency": true, "alignRight": true },
                { "title": "Balance Due", "role": "balance_due", "width": 120, "isCurrency": true, "alignRight": true },
                { "title": "Last Paid", "role": "last_paid_date", "width": 110 },
                { "title": "Fee Status", "role": "fee_status", "width": 100, "isBadge": true },
                { "title": "Actions", "role": "actions", "width": 90, "isAction": true, "actions": ["fees", "whatsapp"], "alignRight": true }
            ]

            onRowDoubleClicked: (rowData, index) => {
                root.openStudentFeeDetails(rowData.student_id || rowData.id);
            }

            onRowAction: (action, rowData, index) => {
                if (action === "fees") {
                    root.selectedStudentForPayment = rowData;
                    feePaymentDrawer.openDrawer(rowData);
                } else if (action === "whatsapp") {
                    if (typeof communicationsPage !== "undefined") {
                        communicationsPage.selectStudentForMessaging(rowData.student_id || rowData.id);
                    }
                    crmBridge.navigateTo("Communications");
                }
            }
        }
    }

    // Quick Record Payment Drawer
    DrawerPanel {
        id: feePaymentDrawer
        title: "Record Installment Payment"
        subtitle: root.selectedStudentForPayment ? `${root.selectedStudentForPayment.name} (${root.selectedStudentForPayment.id_no})` : ""
        primaryActionText: "Record Payment & Print Receipt"
        secondaryActionText: "Cancel"

        function openDrawer(student) {
            root.selectedStudentForPayment = student;
            feePayAmountField.text = student.balance_due > 0 ? String(student.balance_due) : "0";
            feePayReceiptField.text = `REC-${Date.now().toString().slice(-6)}`;
            isOpen = true;
        }

        onPrimaryClicked: {
            if (!root.selectedStudentForPayment) return;
            var amount = parseFloat(feePayAmountField.text) || 0;
            if (amount <= 0) {
                crmBridge.showToast("Please enter a valid payment amount.", "warning", "Validation Error");
                return;
            }

            var res = studentsBridge.recordPayment(
                root.selectedStudentForPayment.student_id,
                0,
                amount,
                feePayDateField.text,
                feePayModeCombo.currentText,
                feePayReceiptField.text,
                "Fee settlement"
            );

            if (res.success) {
                isOpen = false;
                root.refresh();
                crmBridge.showToast(`Recorded payment of ₹${amount.toLocaleString("en-IN")}`, "success", "Payment Recorded");
            }
        }

        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingMD

            FormField {
                id: feePayAmountField
                label: "Amount to Pay"
                required: true
                prefix: "₹"
                text: "0"
            }

            FormField {
                id: feePayDateField
                label: "Payment Date"
                text: Qt.formatDate(new Date(), "yyyy-MM-dd")
            }

            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true
                Text { text: "Payment Mode"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                ComboBox {
                    id: feePayModeCombo
                    Layout.fillWidth: true
                    model: ["Cash", "UPI / QR", "Bank Transfer", "Cheque", "Card"]
                }
            }

            FormField {
                id: feePayReceiptField
                label: "Receipt Number"
                text: ""
            }
        }
    }
}
