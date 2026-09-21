import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property var batchesList: []
    property var staffList: []
    property var coursesList: []
    property var metrics: ({})
    property string searchQuery: ""
    property string statusFilter: "All"

    property var selectedBatchForRoster: null
    property var editingBatch: null
    property var deletingBatch: null

    function refresh() {
        if (typeof staffBridge !== "undefined") {
            batchesList = staffBridge.getBatches("All", statusFilter, searchQuery);
            staffList = staffBridge.getStaffNames();
            metrics = staffBridge.getMetrics();
        }
        if (typeof coursesBridge !== "undefined") {
            coursesList = coursesBridge.getCourseNames();
        }
    }

    Component.onCompleted: refresh()

    Connections {
        target: typeof staffBridge !== "undefined" ? staffBridge : null
        function onBatchesChanged() {
            root.refresh();
            if (root.selectedBatchForRoster) {
                rosterDrawer.loadBatchRoster(root.selectedBatchForRoster.id);
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingMD

        // Header
        PageHeader {
            title: "Batches & Class Schedules"
            subtitle: "Manage course timings, lab room allocations, faculty assignments, and student rosters"
            countText: `${root.batchesList.length} batches`

            PrimaryButton {
                text: "New Batch Schedule"
                iconName: "plus"
                onClicked: batchDrawer.openDrawer(null)
            }
        }

        // Metrics Summary Row
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingMD

            StatCard {
                title: "Active Batches"
                value: String(root.metrics.active_batches || 0)
                subtext: `${root.metrics.total_batches || 0} total scheduled`
                iconName: "batches"
                iconColor: Theme.primary
            }

            StatCard {
                title: "Active Enrollments"
                value: String(root.metrics.active_enrollments || 0)
                subtext: "Students attending live batches"
                iconName: "students"
                iconColor: Theme.accent
            }

            StatCard {
                title: "Instructors & Faculty"
                value: String(root.metrics.active_staff || 0)
                subtext: "Assigned faculty members"
                iconName: "staff"
                iconColor: Theme.info
            }
        }

        // Batches Data Table
        DataTable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: root.batchesList
            pageSize: 15

            columns: [
                { "title": "Batch Code", "role": "batch_code", "width": 110, "isPrimary": true },
                { "title": "Batch Name", "role": "batch_name", "width": 180, "fill": true, "isHighlight": true },
                { "title": "Course", "role": "course_name", "width": 150 },
                { "title": "Instructor", "role": "instructor_name", "width": 150 },
                { "title": "Time Slot", "role": "start_time", "width": 120 },
                { "title": "Days", "role": "days_schedule", "width": 100 },
                { "title": "Room / Lab", "role": "room_lab", "width": 100 },
                { "title": "Enrolled", "role": "enrolled_count", "width": 90, "alignRight": true },
                { "title": "Status", "role": "status", "width": 95, "isBadge": true },
                { "title": "Actions", "role": "actions", "width": 100, "isAction": true, "actions": ["view", "edit", "trash"], "alignRight": true }
            ]

            onRowClicked: (rowData, index) => {
                rosterDrawer.loadBatchRoster(rowData.id);
            }

            onRowAction: (action, rowData, index) => {
                if (action === "view") {
                    rosterDrawer.loadBatchRoster(rowData.id);
                } else if (action === "edit") {
                    batchDrawer.openDrawer(rowData);
                } else if (action === "trash") {
                    root.deletingBatch = rowData;
                    deleteBatchConfirm.isOpen = true;
                }
            }
        }
    }

    // Batch Roster Drawer
    DrawerPanel {
        id: rosterDrawer
        title: root.selectedBatchForRoster ? `Roster: ${root.selectedBatchForRoster.batch_name}` : "Batch Roster"
        subtitle: root.selectedBatchForRoster ? `${root.selectedBatchForRoster.course_name} · ${root.selectedBatchForRoster.start_time} (${root.selectedBatchForRoster.room_lab})` : ""
        drawerWidth: 600
        primaryActionText: "+ Add Student to Batch"
        secondaryActionText: "Close"

        function loadBatchRoster(batchId) {
            root.selectedBatchForRoster = staffBridge.getBatchById(batchId);
            isOpen = true;
        }

        onPrimaryClicked: {
            if (root.selectedBatchForRoster) {
                addStudentModal.openModal(root.selectedBatchForRoster.id);
            }
        }

        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingMD

            DataTable {
                Layout.fillWidth: true
                implicitHeight: 380
                model: root.selectedBatchForRoster ? (root.selectedBatchForRoster.roster || []) : []
                showPagination: false
                emptyTitle: "No Students Enrolled"
                emptyMessage: "Click '+ Add Student to Batch' to enroll active students into this batch schedule."

                columns: [
                    { "title": "ID", "role": "id_no", "width": 100, "isPrimary": true },
                    { "title": "Student Name", "role": "name", "width": 160, "fill": true, "isHighlight": true },
                    { "title": "Mobile", "role": "mobile_no", "width": 110 },
                    { "title": "Fee Dues", "role": "fee_status", "width": 90, "isBadge": true },
                    { "title": "Remove", "role": "actions", "width": 60, "isAction": true, "actions": ["trash"], "alignRight": true }
                ]

                onRowDoubleClicked: (rowData, index) => {
                    if (rowData.student_id) {
                        if (typeof studentDetailsPage !== "undefined") {
                            studentDetailsPage.loadStudent(String(rowData.student_id));
                            studentDetailsPage.activeTab = "Fee Installments";
                        }
                        crmBridge.navigateTo("StudentDetails");
                    }
                }

                onRowAction: (action, rowData, index) => {
                    if (action === "trash" && root.selectedBatchForRoster) {
                        staffBridge.removeStudentFromBatch(root.selectedBatchForRoster.id, String(rowData.student_id));
                        rosterDrawer.loadBatchRoster(root.selectedBatchForRoster.id);
                    }
                }
            }
        }
    }

    // Add Student to Batch Modal
    Item {
        id: addStudentModal
        anchors.fill: parent
        visible: opacity > 0
        opacity: modalOpen ? 1 : 0
        z: 110

        property bool modalOpen: false
        property string batchId: ""
        property var unassignedList: []
        property string studentSearch: ""

        function openModal(bId) {
            batchId = bId;
            studentSearch = "";
            refreshUnassigned();
            modalOpen = true;
        }

        function refreshUnassigned() {
            unassignedList = staffBridge.getUnassignedStudents(batchId, studentSearch);
        }

        Behavior on opacity { NumberAnimation { duration: Theme.animFast } }

        Rectangle {
            anchors.fill: parent
            color: Qt.rgba(0, 0, 0, 0.6)
            MouseArea { anchors.fill: parent; onClicked: addStudentModal.modalOpen = false }
        }

        Rectangle {
            anchors.centerIn: parent
            width: 520
            implicitHeight: 480
            radius: Theme.radiusLG
            color: Theme.surface
            border.color: Theme.border
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingLG
                spacing: Theme.spacingMD

                Text {
                    text: "Enroll Student in Batch"
                    color: Theme.textPrimary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontTitle
                    font.weight: Theme.weightBold
                }

                SearchBar {
                    placeholderText: "Search candidate name or ID..."
                    Layout.fillWidth: true
                    onSearchChanged: query => {
                        addStudentModal.studentSearch = query;
                        addStudentModal.refreshUnassigned();
                    }
                }

                DataTable {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: addStudentModal.unassignedList
                    showPagination: false

                    columns: [
                        { "title": "ID", "role": "id_no", "width": 100, "isPrimary": true },
                        { "title": "Name", "role": "name", "width": 160, "fill": true },
                        { "title": "Course", "role": "course_name", "width": 130 },
                        { "title": "Enroll", "role": "actions", "width": 60, "isAction": true, "actions": ["plus"], "alignRight": true }
                    ]

                    onRowAction: (action, rowData, index) => {
                        if (action === "plus") {
                            staffBridge.enrollStudent(addStudentModal.batchId, String(rowData.id), "");
                            addStudentModal.refreshUnassigned();
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Item { Layout.fillWidth: true }
                    SecondaryButton {
                        text: "Done"
                        onClicked: addStudentModal.modalOpen = false
                    }
                }
            }
        }
    }

    // Add / Edit Batch Drawer
    DrawerPanel {
        id: batchDrawer
        title: root.editingBatch ? "Edit Batch Schedule" : "Create New Batch"
        subtitle: root.editingBatch ? root.editingBatch.batch_code : "Configure batch schedule and room"
        primaryActionText: "Save Batch"
        secondaryActionText: "Cancel"

        function openDrawer(batch) {
            root.editingBatch = batch;
            if (batch) {
                bNameField.text = batch.batch_name || "";
                bTimeField.text = batch.start_time || "09:00 AM";
                bDaysField.text = batch.days_schedule || "Mon-Fri";
                bRoomField.text = batch.room_lab || "Lab 1";
                bCapacityField.text = String(batch.max_capacity || 20);
                bCourseCombo.currentIndex = root.coursesList.indexOf(batch.course_name);
            } else {
                bNameField.text = "";
                bTimeField.text = "09:00 AM - 11:00 AM";
                bDaysField.text = "Mon - Fri";
                bRoomField.text = "Lab 1 (AutoCAD)";
                bCapacityField.text = "20";
            }
            isOpen = true;
        }

        onPrimaryClicked: {
            if (!bNameField.text.trim()) {
                crmBridge.showToast("Batch name is required.", "warning", "Validation Error");
                return;
            }

            var payload = {
                "id": root.editingBatch ? root.editingBatch.id : undefined,
                "batch_name": bNameField.text.trim(),
                "course_name": bCourseCombo.currentText,
                "staff_id": bStaffCombo.currentValue || undefined,
                "start_time": bTimeField.text.trim(),
                "days_schedule": bDaysField.text.trim(),
                "room_lab": bRoomField.text.trim(),
                "max_capacity": parseInt(bCapacityField.text) || 20,
                "status": "Active"
            };

            var res = staffBridge.saveBatch(JSON.stringify(payload));
            if (res.success) {
                isOpen = false;
                root.refresh();
                crmBridge.showToast(res.message, "success", "Saved");
            } else {
                crmBridge.showToast(res.message, "error", "Save Failed");
            }
        }

        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingMD

            FormField {
                id: bNameField
                label: "Batch Name"
                required: true
                placeholder: "e.g. AutoCAD Morning Batch A-24"
            }

            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true
                Text { text: "Course"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                ComboBox {
                    id: bCourseCombo
                    Layout.fillWidth: true
                    model: root.coursesList
                }
            }

            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true
                Text { text: "Assigned Instructor"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall }
                ComboBox {
                    id: bStaffCombo
                    Layout.fillWidth: true
                    textRole: "name"
                    valueRole: "id"
                    model: root.staffList
                }
            }

            FormField {
                id: bTimeField
                label: "Timing / Schedule"
                text: "09:00 AM - 11:00 AM"
            }

            FormField {
                id: bDaysField
                label: "Days"
                text: "Mon - Fri"
            }

            FormField {
                id: bRoomField
                label: "Room / Computer Lab"
                text: "Lab 1"
            }

            FormField {
                id: bCapacityField
                label: "Max Capacity"
                text: "20"
            }
        }
    }

    // Confirm Delete Batch Dialog
    ConfirmDialog {
        id: deleteBatchConfirm
        title: "Delete Batch"
        message: root.deletingBatch ? `Are you sure you want to delete batch "${root.deletingBatch.batch_name}"?` : ""
        confirmText: "Delete Batch"
        onConfirmed: {
            if (root.deletingBatch) {
                var ok = staffBridge.deleteBatch(root.deletingBatch.id);
                if (ok) {
                    crmBridge.showToast("Batch deleted.", "success", "Deleted");
                    root.refresh();
                }
            }
        }
    }
}
