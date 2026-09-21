import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"
import "../components"

Item {
    id: root

    property var coursesList: []
    property var categoriesList: []
    property var metrics: ({})
    property string searchQuery: ""
    property string categoryFilter: "All"
    property string statusFilter: "All"

    property var editingCourse: null
    property var deletingCourse: null

    function refresh() {
        if (typeof coursesBridge !== "undefined") {
            coursesList = coursesBridge.getCourses(searchQuery, categoryFilter, statusFilter);
            categoriesList = ["All"].concat(coursesBridge.getCategories());
            metrics = coursesBridge.getMetrics();
        }
    }

    Component.onCompleted: refresh()

    Connections {
        target: typeof coursesBridge !== "undefined" ? coursesBridge : null
        function onCoursesChanged() {
            root.refresh();
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLG
        spacing: Theme.spacingMD

        // Header
        PageHeader {
            title: "Course Catalog & Curricula"
            subtitle: "Manage engineering, architectural, IT, and multimedia training programs"
            countText: `${root.coursesList.length} courses`

            SecondaryButton {
                text: "Seed Defaults"
                iconName: "refresh"
                onClicked: {
                    var count = coursesBridge.seedDefaults();
                    crmBridge.showToast(`Catalog synchronized.`, "info", "Courses Synced");
                    root.refresh();
                }
            }

            PrimaryButton {
                text: "New Course"
                iconName: "plus"
                onClicked: courseDrawer.openDrawer(null)
            }
        }

        // Metrics Summary Row
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingMD

            StatCard {
                title: "Total Programs"
                value: String(root.metrics.total_courses || root.coursesList.length)
                subtext: `${root.metrics.active_courses || 0} active in catalog`
                iconName: "courses"
                iconColor: Theme.primary
            }

            StatCard {
                title: "Average Fee"
                value: "₹" + Math.round(root.metrics.avg_fee || 0).toLocaleString("en-IN")
                subtext: "Standard tuition pricing"
                iconName: "fees"
                iconColor: Theme.accent
            }

            StatCard {
                title: "Categories"
                value: String(root.metrics.categories_count || 0)
                subtext: "Architecture, IT, Design, Civil"
                iconName: "chart"
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
                    placeholderText: "Search course name, code, or description..."
                    implicitWidth: 320
                    onSearchChanged: query => {
                        root.searchQuery = query;
                        root.refresh();
                    }
                }

                FilterBar {
                    Layout.fillWidth: true
                    options: root.categoriesList.length > 0 ? root.categoriesList : ["All"]
                    selectedOption: root.categoryFilter
                    onSelectionChanged: opt => {
                        root.categoryFilter = opt;
                        root.refresh();
                    }
                }
            }
        }

        // Courses Data Table
        DataTable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: root.coursesList
            pageSize: 15

            columns: [
                { "title": "Code", "role": "course_code", "width": 110, "isPrimary": true },
                { "title": "Course Name", "role": "name", "width": 200, "fill": true, "isHighlight": true },
                { "title": "Category", "role": "category", "width": 160 },
                { "title": "Standard Fee", "role": "standard_fee", "width": 120, "isCurrency": true, "alignRight": true },
                { "title": "Enrolled", "role": "student_count", "width": 90, "alignRight": true },
                { "title": "Batches", "role": "batch_count", "width": 90, "alignRight": true },
                { "title": "Status", "role": "status", "width": 100, "isBadge": true },
                { "title": "Actions", "role": "actions", "width": 90, "isAction": true, "actions": ["edit", "trash"], "alignRight": true }
            ]

            onRowClicked: (rowData, index) => {
                courseDrawer.openDrawer(rowData);
            }

            onRowDoubleClicked: (rowData, index) => {
                courseDrawer.openDrawer(rowData);
            }

            onRowAction: (action, rowData, index) => {
                if (action === "edit") {
                    courseDrawer.openDrawer(rowData);
                } else if (action === "trash") {
                    root.deletingCourse = rowData;
                    deleteCourseConfirm.isOpen = true;
                }
            }
        }
    }

    // Add / Edit Course Drawer
    DrawerPanel {
        id: courseDrawer
        title: root.editingCourse ? "Edit Course Program" : "Create New Course"
        subtitle: root.editingCourse ? root.editingCourse.course_code : "Add course to training catalog"
        primaryActionText: "Save Course"
        secondaryActionText: "Cancel"

        function openDrawer(course) {
            root.editingCourse = course;
            if (course) {
                codeField.text = course.course_code || "";
                nameField.text = course.name || "";
                var cIdx = catCombo.indexOfValue(course.category || "");
                if (cIdx >= 0) {
                    catCombo.currentIndex = cIdx;
                } else {
                    catCombo.editText = course.category || "General";
                }
                feeField.text = String(course.standard_fee || 0);
                descField.text = course.description || "";
            } else {
                nameField.text = "";
                if (catCombo.count > 0) catCombo.currentIndex = 0;
                var initialCat = catCombo.currentText || "Architecture & Civil";
                if (typeof coursesBridge !== "undefined") {
                    codeField.text = coursesBridge.generateCourseCode(initialCat);
                } else {
                    codeField.text = "CRS-ARCH-01";
                }
                feeField.text = "35000";
                descField.text = "";
            }
            isOpen = true;
        }

        onPrimaryClicked: {
            if (!nameField.text.trim()) {
                crmBridge.showToast("Course name is mandatory.", "warning", "Validation Error");
                return;
            }

            var catVal = catCombo.currentText ? catCombo.currentText.trim() : (catCombo.editText ? catCombo.editText.trim() : "General");

            var payload = {
                "id": root.editingCourse ? root.editingCourse.id : undefined,
                "course_code": codeField.text.trim(),
                "name": nameField.text.trim(),
                "category": catVal,
                "standard_fee": parseFloat(feeField.text) || 0.0,
                "description": descField.text.trim(),
                "status": "Active"
            };

            var res = coursesBridge.saveCourse(JSON.stringify(payload));
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
                id: nameField
                label: "Course Title"
                required: true
                placeholder: "e.g. Master Architecture"
            }

            FormField {
                id: codeField
                label: "Course Code"
                placeholder: "Auto-generated e.g. CRS-ARCH-01"
            }

            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true

                RowLayout {
                    Text { text: "Category"; color: Theme.textSecondary; font.pixelSize: Theme.fontSmall; font.weight: Theme.weightMedium }
                    Text { text: "*"; color: Theme.danger; font.pixelSize: Theme.fontSmall; font.weight: Theme.weightBold }
                }

                ComboBox {
                    id: catCombo
                    Layout.fillWidth: true
                    editable: true
                    model: {
                        var list = root.categoriesList.filter(c => c !== "All");
                        return list.length > 0 ? list : [
                            "Architecture & Civil",
                            "Civil & Survey",
                            "Interior Design",
                            "Data & AI",
                            "IT & Programming",
                            "Drafting & CAD",
                            "Digital Marketing",
                            "Multimedia & Graphics",
                            "Accounting & Finance",
                            "Computer Applications",
                            "Foundational IT",
                            "Mechanical & Design",
                            "General"
                        ];
                    }
                    onActivated: index => {
                        if (!root.editingCourse && typeof coursesBridge !== "undefined") {
                            codeField.text = coursesBridge.generateCourseCode(currentText);
                        }
                    }
                }
            }

            FormField {
                id: feeField
                label: "Standard Course Fee"
                prefix: "₹"
                required: true
                text: "35000"
            }

            FormField {
                id: descField
                label: "Curriculum Description"
                isMultiline: true
                placeholder: "Detailed module and software syllabus overview"
            }
        }
    }

    // Confirm Delete Course Dialog
    ConfirmDialog {
        id: deleteCourseConfirm
        title: "Delete Course"
        message: root.deletingCourse ? `Are you sure you want to delete course "${root.deletingCourse.name}"?` : ""
        confirmText: "Delete Course"
        onConfirmed: {
            if (root.deletingCourse) {
                var ok = coursesBridge.deleteCourse(root.deletingCourse.id);
                if (ok) {
                    crmBridge.showToast("Course deleted from catalog.", "success", "Deleted");
                    root.refresh();
                }
            }
        }
    }
}
