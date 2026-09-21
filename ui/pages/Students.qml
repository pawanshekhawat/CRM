import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property var studentsList: []
    property string searchQuery: ""
    property string statusFilter: "All"
    property string courseFilter: "All"
    property string feeFilter: "All"
    property string sortBy: "fee_date_desc"
    property string sortColumnRole: "last_paid_date_str"
    property string sortDirection: "desc"

    property var selectedStudentForPayment: null

    function setSort(key, role, dir) {
        root.sortBy = key;
        root.sortColumnRole = role || "";
        root.sortDirection = dir || "desc";
        if (typeof sortCombo !== "undefined" && sortCombo.model) {
            for (var i = 0; i < sortCombo.model.length; i++) {
                if (sortCombo.model[i].value === key) {
                    sortCombo.currentIndex = i;
                    break;
                }
            }
        }
        root.refresh();
    }

    function refresh() {
        if (typeof studentsBridge !== "undefined") {
            studentsList = studentsBridge.getStudents(
                searchQuery,
                statusFilter,
                courseFilter,
                feeFilter,
                sortBy
            );
        }
    }

    Component.onCompleted: refresh()

    Connections {
        target: typeof studentsBridge !== "undefined" ? studentsBridge : null
        function onStudentsChanged() {
            root.refresh();
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingMD

        // Page Header
        PageHeader {
            title: "Students & Admissions"
            subtitle: "Manage student enrollments, academic progress, and fee balances"
            countText: `${root.studentsList.length} students`

            SecondaryButton {
                text: "Export Excel"
                iconName: "download"
                onClicked: {
                    var path = studentsBridge.exportToExcel(searchQuery, statusFilter, courseFilter, feeFilter);
                    if (path) {
                        crmBridge.showToast(`Exported ${root.studentsList.length} records to Excel.`, "success", "Excel Exported");
                    }
                }
            }

            PrimaryButton {
                text: "New Admission"
                iconName: "plus"
                onClicked: {
                    if (typeof admissionsPage !== "undefined") {
                        admissionsPage.resetForm();
                    }
                    crmBridge.navigateTo("Admissions");
                }
            }
        }

        // Search & Filter Toolbar
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

                SearchBar {
                    placeholderText: "Search by Name, ID, Mobile, or Course..."
                    implicitWidth: 280
                    onSearchChanged: query => {
                        root.searchQuery = query;
                        root.refresh();
                    }
                }

                FilterBar {
                    options: ["All", "Active", "Completed", "Dropped"]
                    selectedOption: root.statusFilter
                    onSelectionChanged: opt => {
                        root.statusFilter = opt;
                        root.refresh();
                    }
                }

                FilterBar {
                    options: ["All Dues", "Paid", "Partial", "Pending"]
                    selectedOption: root.feeFilter === "All" ? "All Dues" : root.feeFilter
                    onSelectionChanged: opt => {
                        root.feeFilter = (opt === "All Dues") ? "All" : opt;
                        root.refresh();
                    }
                }

                Item { Layout.fillWidth: true }

                // Sort By Selector
                Rectangle {
                    implicitHeight: 36
                    implicitWidth: 235
                    radius: Theme.radiusMD
                    color: Theme.surfaceElevated
                    border.color: Theme.border
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        spacing: 6

                        Icon {
                            name: "sort"
                            size: 14
                            color: Theme.primary
                            Layout.alignment: Qt.AlignVCenter
                        }

                        ComboBox {
                            id: sortCombo
                            Layout.fillWidth: true
                            implicitHeight: 32
                            model: [
                                { "text": "Fee Date: Recent First", "value": "fee_date_desc", "role": "last_paid_date_str", "dir": "desc" },
                                { "text": "Fee Date: Oldest First", "value": "fee_date_asc", "role": "last_paid_date_str", "dir": "asc" },
                                { "text": "Balance Due: High to Low", "value": "due_desc", "role": "fee_status_display", "dir": "desc" },
                                { "text": "Balance Due: Low to High", "value": "due_asc", "role": "fee_status_display", "dir": "asc" },
                                { "text": "Student Name (A to Z)", "value": "name_asc", "role": "name", "dir": "asc" },
                                { "text": "Student Name (Z to A)", "value": "name_desc", "role": "name", "dir": "desc" },
                                { "text": "Student ID (Default)", "value": "id_no", "role": "", "dir": "asc" },
                                { "text": "Admission Date (Newest)", "value": "latest", "role": "", "dir": "desc" }
                            ]
                            textRole: "text"
                            valueRole: "value"
                            currentIndex: 0

                            onActivated: (index) => {
                                var item = model[index];
                                root.sortBy = item.value;
                                root.sortColumnRole = item.role || "";
                                root.sortDirection = item.dir || "desc";
                                root.refresh();
                            }

                            background: Item {}

                            contentItem: Text {
                                text: sortCombo.displayText
                                color: Theme.textPrimary
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSmall
                                font.weight: Theme.weightMedium
                                elide: Text.ElideRight
                                verticalAlignment: Text.AlignVCenter
                            }

                            popup: Popup {
                                y: sortCombo.height + 6
                                width: Math.max(sortCombo.width + 30, 240)
                                implicitHeight: Math.min(320, contentItem.implicitHeight + 12)
                                padding: 6
                                background: Rectangle {
                                    radius: Theme.radiusMD
                                    color: Theme.surfaceElevated
                                    border.color: Theme.border
                                    border.width: 1
                                }
                                contentItem: ListView {
                                    clip: true
                                    implicitHeight: contentHeight
                                    model: sortCombo.popup.visible ? sortCombo.delegateModel : null
                                    currentIndex: sortCombo.highlightedIndex
                                    ScrollIndicator.vertical: ScrollIndicator { }
                                }
                            }

                            delegate: ItemDelegate {
                                id: sortItemDel
                                width: sortCombo.width + 18
                                implicitHeight: 32
                                highlighted: sortCombo.highlightedIndex === index

                                background: Rectangle {
                                    radius: Theme.radiusSM
                                    color: sortItemDel.highlighted || sortItemDel.hovered ? Theme.primarySoft : "transparent"
                                }

                                contentItem: Text {
                                    text: modelData.text || ""
                                    color: (sortCombo.currentIndex === index) ? Theme.primaryText :
                                           (sortItemDel.highlighted ? Theme.textPrimary : Theme.textSecondary)
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSmall
                                    font.weight: (sortCombo.currentIndex === index) ? Theme.weightDemiBold : Theme.weightNormal
                                    verticalAlignment: Text.AlignVCenter
                                    anchors.leftMargin: 8
                                }
                            }
                        }
                    }
                }

                SecondaryButton {
                    text: "Reset"
                    iconName: "refresh"
                    customHeight: 34
                    onClicked: {
                        root.searchQuery = "";
                        root.statusFilter = "All";
                        root.feeFilter = "All";
                        root.courseFilter = "All";
                        root.setSort("fee_date_desc", "last_paid_date_str", "desc");
                    }
                }
            }
        }

        // Students Data Table
        DataTable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: root.studentsList
            showPagination: false
            activeSortRole: root.sortColumnRole
            activeSortDirection: root.sortDirection

            columns: [
                { "title": "Student", "role": "name", "width": 210, "fill": true, "isAvatarWithName": true },
                { "title": "Contact Number", "role": "mobile_no", "width": 120, "isMuted": true },
                { "title": "Course Enrolled", "role": "course_name", "width": 150 },
                { "title": "Last Fee Paid", "role": "last_paid_date_str", "subtitleRole": "days_ago_str", "width": 140, "isDateWithSubtitle": true },
                { "title": "Fee Status", "role": "fee_status_display", "width": 150, "isBadge": true },
                { "title": "Status", "role": "status", "width": 115, "isStatusDropdown": true },
                { "title": "Actions", "role": "actions", "width": 165, "isAction": true, "actions": ["eye", "edit", "fees", "whatsapp", "download"], "alignRight": true }
            ]

            onStatusChanged: (rowData, newStatus, index) => {
                var res = studentsBridge.updateStudentStatus(rowData.id, newStatus);
                if (res) {
                    crmBridge.showToast(`Updated status to "${newStatus}" for ${rowData.name}`, "success", "Status Updated");
                    root.refresh();
                } else {
                    crmBridge.showToast("Failed to update student status.", "error", "Update Error");
                }
            }

            onHeaderClicked: (colDef, index) => {
                if (colDef.role === "last_paid_date_str" || colDef.title === "Last Fee Paid") {
                    if (root.sortBy === "fee_date_desc") {
                        root.setSort("fee_date_asc", "last_paid_date_str", "asc");
                    } else {
                        root.setSort("fee_date_desc", "last_paid_date_str", "desc");
                    }
                } else if (colDef.role === "name" || colDef.title === "Student") {
                    if (root.sortBy === "name_asc") {
                        root.setSort("name_desc", "name", "desc");
                    } else {
                        root.setSort("name_asc", "name", "asc");
                    }
                } else if (colDef.role === "fee_status_display" || colDef.title === "Fee Status") {
                    if (root.sortBy === "due_desc") {
                        root.setSort("due_asc", "fee_status_display", "asc");
                    } else {
                        root.setSort("due_desc", "fee_status_display", "desc");
                    }
                } else if (colDef.role === "course_name" || colDef.title === "Course Enrolled") {
                    if (root.sortBy === "course") {
                        root.setSort("course_desc", "course_name", "desc");
                    } else {
                        root.setSort("course", "course_name", "asc");
                    }
                } else if (colDef.role === "mobile_no" || colDef.title === "Contact Number") {
                    if (root.sortBy === "mobile") {
                        root.setSort("mobile_desc", "mobile_no", "desc");
                    } else {
                        root.setSort("mobile", "mobile_no", "asc");
                    }
                } else if (colDef.role === "status" || colDef.title === "Status") {
                    if (root.sortBy === "status") {
                        root.setSort("status_desc", "status", "desc");
                    } else {
                        root.setSort("status", "status", "asc");
                    }
                }
            }

            onRowClicked: (rowData, index) => {
                root.openStudentDetails(rowData.id, "Overview");
            }

            onRowDoubleClicked: (rowData, index) => {
                root.openStudentDetails(rowData.id, "Fee Installments");
            }

            onRowAction: (action, rowData, index) => {
                if (action === "view" || action === "eye") {
                    root.openStudentDetails(rowData.id, "Overview");
                } else if (action === "edit") {
                    if (typeof admissionsPage !== "undefined") {
                        admissionsPage.loadStudentForEdit(rowData.id);
                    }
                    crmBridge.navigateTo("Admissions");
                } else if (action === "fees") {
                    root.selectedStudentForPayment = rowData;
                    paymentDrawer.openDrawer(rowData);
                } else if (action === "whatsapp" || action === "messaging") {
                    if (typeof communicationsPage !== "undefined") {
                        communicationsPage.selectStudentForMessaging(rowData);
                    }
                    crmBridge.navigateTo("Communications");
                } else if (action === "download") {
                    var pdf = studentsBridge.generateAdmissionPdf(rowData.id);
                    if (pdf) {
                        crmBridge.showToast(`Admission slip generated for ${rowData.name}`, "success", "PDF Ready");
                        reportsBridge.openDocument(pdf);
                    }
                }
            }

            onEmptyActionClicked: {
                root.searchQuery = "";
                root.statusFilter = "All";
                root.feeFilter = "All";
                root.setSort("fee_date_desc", "last_paid_date_str", "desc");
            }
        }
    }

    function openStudentDetails(studentId, defaultTab) {
        if (!studentId) return;
        if (typeof studentDetailsPage !== "undefined") {
            studentDetailsPage.loadStudent(String(studentId));
            studentDetailsPage.activeTab = defaultTab || "Overview";
        }
        crmBridge.navigateTo("StudentDetails");
    }

    // Quick Record Payment Drawer
    DrawerPanel {
        id: paymentDrawer
        title: "Record Fee Payment"
        subtitle: root.selectedStudentForPayment ? `${root.selectedStudentForPayment.name} (${root.selectedStudentForPayment.id_no})` : ""
        primaryActionText: "Save Payment & Receipt"
        secondaryActionText: "Cancel"

        property int installmentId: 0
        property string paymentDate: ""

        function openDrawer(student) {
            root.selectedStudentForPayment = student;
            payAmountField.text = student.balance_due > 0 ? String(student.balance_due) : "0";
            payRemarksField.text = "Fee installment payment";
            payReceiptField.text = `REC-${Date.now().toString().slice(-6)}`;
            isOpen = true;
        }

        onPrimaryClicked: {
            if (!root.selectedStudentForPayment) return;
            var amount = parseFloat(payAmountField.text) || 0;
            if (amount <= 0) {
                crmBridge.showToast("Please enter a valid payment amount.", "warning", "Validation Error");
                return;
            }

            var res = studentsBridge.recordPayment(
                root.selectedStudentForPayment.id,
                0,
                amount,
                payDateField.text,
                payModeCombo.currentText,
                payReceiptField.text,
                payRemarksField.text
            );

            if (res.success) {
                isOpen = false;
                root.refresh();
                crmBridge.showToast(`Recorded payment of ₹${amount.toLocaleString("en-IN")}`, "success", "Payment Saved");
            }
        }

        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingMD

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 80
                radius: Theme.radiusMD
                color: Theme.surfaceElevated
                border.color: Theme.borderSubtle
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingMD
                    spacing: Theme.spacingMD

                    ColumnLayout {
                        Layout.fillWidth: true
                        Text { text: "Outstanding Balance"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                        Text {
                            text: root.selectedStudentForPayment ? "₹" + Number(root.selectedStudentForPayment.balance_due || 0).toLocaleString("en-IN") : "₹0"
                            color: Theme.dangerText
                            font.pixelSize: Theme.fontTitle
                            font.weight: Theme.weightBold
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Text { text: "Course"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                        Text {
                            text: root.selectedStudentForPayment ? root.selectedStudentForPayment.course_name : ""
                            color: Theme.textPrimary
                            font.pixelSize: Theme.fontBody
                            font.weight: Theme.weightMedium
                            elide: Text.ElideRight
                        }
                    }
                }
            }

            FormField {
                id: payAmountField
                label: "Amount to Pay"
                required: true
                prefix: "₹"
                text: "0"
            }

            FormField {
                id: payDateField
                label: "Payment Date"
                text: Qt.formatDate(new Date(), "yyyy-MM-dd")
                placeholder: "YYYY-MM-DD"
            }

            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true

                Text {
                    text: "Payment Mode"
                    color: Theme.textSecondary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSmall
                    font.weight: Theme.weightMedium
                }

                ComboBox {
                    id: payModeCombo
                    Layout.fillWidth: true
                    model: ["Cash", "UPI / QR", "Bank Transfer", "Cheque", "Card"]
                }
            }

            FormField {
                id: payReceiptField
                label: "Receipt / Reference No"
                text: ""
            }

            FormField {
                id: payRemarksField
                label: "Remarks / Notes"
                isMultiline: true
                text: ""
            }
        }
    }
}
