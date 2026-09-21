import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property var staffList: []
    property var metrics: ({})
    property string searchQuery: ""
    property string deptFilter: "All"
    property string statusFilter: "All"

    property var editingStaff: null
    property var deletingStaff: null

    function refresh() {
        if (typeof staffBridge !== "undefined") {
            staffList = staffBridge.getStaffList(searchQuery, deptFilter, statusFilter);
            metrics = staffBridge.getMetrics();
        }
    }

    Component.onCompleted: refresh()

    Connections {
        target: typeof staffBridge !== "undefined" ? staffBridge : null
        function onStaffChanged() {
            root.refresh();
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingMD

        // Header
        PageHeader {
            title: "Staff & Faculty Directory"
            subtitle: "Manage instructors, faculty members, administrative staff, and student mentoring assignments"
            countText: `${root.staffList.length} members`

            PrimaryButton {
                text: "New Staff Member"
                iconName: "plus"
                onClicked: staffDrawer.openDrawer(null)
            }
        }

        // Metrics Summary
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingMD

            StatCard {
                title: "Total Faculty & Staff"
                value: String(root.metrics.total_staff || root.staffList.length)
                subtext: `${root.metrics.active_staff || 0} active members`
                iconName: "staff"
                iconColor: Theme.primary
            }

            StatCard {
                title: "Total Batches Handled"
                value: String(root.metrics.total_batches || 0)
                subtext: "Live active schedules"
                iconName: "batches"
                iconColor: Theme.accent
            }

            StatCard {
                title: "Active Students Mentored"
                value: String(root.metrics.active_enrollments || 0)
                subtext: "Direct faculty mentoring"
                iconName: "students"
                iconColor: Theme.info
            }
        }

        // Filter Toolbar
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
                    placeholderText: "Search staff name, ID, or phone..."
                    implicitWidth: 320
                    onSearchChanged: query => {
                        root.searchQuery = query;
                        root.refresh();
                    }
                }

                FilterBar {
                    options: ["All", "Active", "Inactive"]
                    selectedOption: root.statusFilter
                    onSelectionChanged: opt => {
                        root.statusFilter = opt;
                        root.refresh();
                    }
                }

                Item { Layout.fillWidth: true }
            }
        }

        // Staff Data Table
        DataTable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: root.staffList
            pageSize: 15

            columns: [
                { "title": "Staff ID", "role": "staff_id", "width": 100, "isPrimary": true },
                { "title": "Staff Name", "role": "name", "width": 180, "fill": true, "isHighlight": true },
                { "title": "Designation", "role": "designation", "width": 150 },
                { "title": "Department", "role": "department", "width": 130 },
                { "title": "Mobile Number", "role": "mobile_no", "width": 130 },
                { "title": "Batches", "role": "batch_count", "width": 90, "alignRight": true },
                { "title": "Mentored", "role": "assigned_student_count", "width": 90, "alignRight": true },
                { "title": "Status", "role": "status", "width": 95, "isBadge": true },
                { "title": "Actions", "role": "actions", "width": 90, "isAction": true, "actions": ["edit", "trash"], "alignRight": true }
            ]

            onRowAction: (action, rowData, index) => {
                if (action === "edit") {
                    staffDrawer.openDrawer(rowData);
                } else if (action === "trash") {
                    root.deletingStaff = rowData;
                    deleteStaffConfirm.isOpen = true;
                }
            }
        }
    }

    // Add / Edit Staff Drawer
    DrawerPanel {
        id: staffDrawer
        title: root.editingStaff ? "Edit Staff Member" : "Register New Staff"
        subtitle: root.editingStaff ? root.editingStaff.staff_id : "Create staff account and assign designation"
        primaryActionText: "Save Staff"
        secondaryActionText: "Cancel"

        function openDrawer(staff) {
            root.editingStaff = staff;
            if (staff) {
                stfNameField.text = staff.name || "";
                stfCodeField.text = staff.staff_id || "";
                stfDesigField.text = staff.designation || "";
                stfDeptField.text = staff.department || "Academics";
                stfPhoneField.text = staff.mobile_no || "";
                stfEmailField.text = staff.email || "";
            } else {
                stfNameField.text = "";
                stfCodeField.text = "";
                stfDesigField.text = "Faculty / Trainer";
                stfDeptField.text = "Academics";
                stfPhoneField.text = "";
                stfEmailField.text = "";
            }
            isOpen = true;
        }

        onPrimaryClicked: {
            if (!stfNameField.text.trim()) {
                crmBridge.showToast("Staff name is mandatory.", "warning", "Validation Error");
                return;
            }

            var payload = {
                "id": root.editingStaff ? root.editingStaff.id : undefined,
                "staff_id": stfCodeField.text.trim(),
                "name": stfNameField.text.trim(),
                "designation": stfDesigField.text.trim(),
                "department": stfDeptField.text.trim(),
                "mobile_no": stfPhoneField.text.trim(),
                "email": stfEmailField.text.trim(),
                "status": "Active"
            };

            var res = staffBridge.saveStaff(JSON.stringify(payload));
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
                id: stfNameField
                label: "Full Name"
                required: true
                placeholder: "e.g. Ramgopal Kumawat Ji"
            }

            FormField {
                id: stfCodeField
                label: "Staff ID Code"
                placeholder: "e.g. STF-001 (leave empty for auto)"
            }

            FormField {
                id: stfDesigField
                label: "Designation"
                placeholder: "e.g. Senior CAD Trainer / Faculty"
            }

            FormField {
                id: stfDeptField
                label: "Department"
                placeholder: "e.g. Civil / Architecture / IT"
            }

            FormField {
                id: stfPhoneField
                label: "Mobile Number"
                placeholder: "Official contact phone"
            }

            FormField {
                id: stfEmailField
                label: "Email Address"
                placeholder: "staff@caddesk.com"
            }
        }
    }

    // Confirm Delete Staff Dialog
    ConfirmDialog {
        id: deleteStaffConfirm
        title: "Delete Staff Member"
        message: root.deletingStaff ? `Are you sure you want to delete staff member "${root.deletingStaff.name}"?` : ""
        confirmText: "Delete Staff"
        onConfirmed: {
            if (root.deletingStaff) {
                var ok = staffBridge.deleteStaff(root.deletingStaff.id);
                if (ok) {
                    crmBridge.showToast("Staff member deleted.", "success", "Deleted");
                    root.refresh();
                }
            }
        }
    }
}
