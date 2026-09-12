from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.modules.students.controllers import StudentController

class CustomFieldsDialog(QDialog):
    """Dialog to create, view, and delete dynamic custom fields for Students."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Custom Fields (Extensible Schema)")
        self.setMinimumSize(680, 480)
        self.resize(720, 520)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Info
        header = QLabel("Dynamic Custom Fields")
        header.setObjectName("headerTitle")
        main_layout.addWidget(header)

        desc = QLabel("Add custom inputs (e.g. Blood Group, Previous Degree, Batch Time) that will dynamically appear on student forms.")
        desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        main_layout.addWidget(desc)

        # Existing Fields Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Field Label", "System Name", "Field Type", "Required", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)

        # Add New Field Section Frame
        add_box = QFrame()
        add_box.setObjectName("card")
        add_layout = QVBoxLayout(add_box)
        add_layout.setContentsMargins(14, 12, 14, 12)
        add_layout.setSpacing(10)

        add_title = QLabel("Add New Custom Field")
        add_title.setObjectName("sectionTitle")
        add_layout.addWidget(add_title)

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(8)

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Field Label (e.g. Blood Group)")
        inputs_layout.addWidget(self.label_input, 2)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Text", "Number", "Date", "Select", "Checkbox", "Textarea"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        inputs_layout.addWidget(self.type_combo, 1)

        self.options_input = QLineEdit()
        self.options_input.setPlaceholderText("Options (comma-separated for Select)")
        self.options_input.setEnabled(False)
        inputs_layout.addWidget(self.options_input, 2)

        self.req_check = QCheckBox("Required")
        inputs_layout.addWidget(self.req_check)

        add_btn = QPushButton("+ Add Field")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self._add_field)
        inputs_layout.addWidget(add_btn)

        add_layout.addLayout(inputs_layout)
        main_layout.addWidget(add_box)

        # Bottom Close Button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        close_btn = QPushButton("Done")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        main_layout.addLayout(btn_box)

        self._load_fields()

    def _on_type_changed(self, text: str):
        self.options_input.setEnabled(text.lower() == "select")

    def _load_fields(self):
        self.table.setRowCount(0)
        defs = StudentController.get_custom_field_definitions("student")

        for row_idx, df in enumerate(defs):
            self.table.insertRow(row_idx)

            label_item = QTableWidgetItem(df.field_label)
            name_item = QTableWidgetItem(df.field_name)
            type_item = QTableWidgetItem(df.field_type.capitalize())
            req_item = QTableWidgetItem("Yes" if df.is_required else "No")

            label_item.setFlags(label_item.flags() ^ Qt.ItemIsEditable)
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            type_item.setFlags(type_item.flags() ^ Qt.ItemIsEditable)
            req_item.setFlags(req_item.flags() ^ Qt.ItemIsEditable)

            self.table.setItem(row_idx, 0, label_item)
            self.table.setItem(row_idx, 1, name_item)
            self.table.setItem(row_idx, 2, type_item)
            self.table.setItem(row_idx, 3, req_item)

            # Delete Button
            del_btn = QPushButton("Delete")
            del_btn.setObjectName("dangerBtn")
            del_btn.setFixedSize(65, 26)
            del_btn.clicked.connect(lambda checked=False, fid=df.id: self._delete_field(fid))
            self.table.setCellWidget(row_idx, 4, del_btn)

    def _add_field(self):
        label = self.label_input.text().strip()
        if not label:
            QMessageBox.warning(self, "Validation Error", "Please enter a field label.")
            return

        f_type = self.type_combo.currentText().lower()
        options = None
        if f_type == "select":
            raw_opts = self.options_input.text().strip()
            if raw_opts:
                options = [opt.strip() for opt in raw_opts.split(",") if opt.strip()]

        StudentController.save_custom_field_definition(
            field_label=label,
            field_type=f_type,
            options=options,
            is_required=self.req_check.isChecked(),
            entity_type="student",
        )

        self.label_input.clear()
        self.options_input.clear()
        self.req_check.setChecked(False)
        self._load_fields()

    def _delete_field(self, field_id: str):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this custom field? Existing values for this field on students will be removed.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            StudentController.delete_custom_field_definition(field_id)
            self._load_fields()
