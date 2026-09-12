from datetime import date
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.staff import Batch
from app.modules.staff.controllers import StaffController

class BatchFormDialog(QDialog):
    """Dialog to create or edit a Batch schedule and assign an instructor."""

    def __init__(self, batch: Optional[Batch] = None, preselected_staff_id: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.batch = batch
        self.is_edit_mode = batch is not None
        self.preselected_staff_id = preselected_staff_id

        self.setWindowTitle("Edit Batch Schedule" if self.is_edit_mode else "➕ Create New Training Batch")
        self.setMinimumSize(620, 560)
        self.resize(680, 600)

        self._build_ui()
        if self.is_edit_mode:
            self._load_batch_data()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        sec_title = QLabel("📚 Batch & Scheduling Details")
        sec_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #F1F5F9;")
        card_layout.addWidget(sec_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        # Row 0: Batch Code & Status
        grid.addWidget(QLabel("Batch Code: *"), 0, 0)
        self.code_input = QLineEdit()
        if not self.is_edit_mode:
            self.code_input.setText(StaffController.generate_next_batch_code())
        self.code_input.setPlaceholderText("e.g. ARCH-M-01")
        grid.addWidget(self.code_input, 0, 1)

        grid.addWidget(QLabel("Status:"), 0, 2)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Upcoming", "Completed", "Suspended"])
        grid.addWidget(self.status_combo, 0, 3)

        # Row 1: Batch Name (Full Width)
        grid.addWidget(QLabel("Batch Title / Name: *"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Morning Architecture Master 9AM")
        grid.addWidget(self.name_input, 1, 1, 1, 3)

        # Row 2: Course & Instructor
        grid.addWidget(QLabel("Course:"), 2, 0)
        self.course_combo = QComboBox()
        self.course_combo.setEditable(False)
        self._populate_course_combo()
        grid.addWidget(self.course_combo, 2, 1)

        grid.addWidget(QLabel("Assigned Faculty: *"), 2, 2)
        self.staff_combo = QComboBox()
        self._populate_staff_combo()
        grid.addWidget(self.staff_combo, 2, 3)

        # Row 3: Timings (Start Time & End Time)
        grid.addWidget(QLabel("Start Time:"), 3, 0)
        self.start_time_combo = QComboBox()
        self.start_time_combo.setEditable(True)
        self.start_time_combo.addItems([
            "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM",
            "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM",
            "05:00 PM", "06:00 PM", "07:00 PM"
        ])
        self.start_time_combo.setCurrentText("09:00 AM")
        grid.addWidget(self.start_time_combo, 3, 1)

        grid.addWidget(QLabel("End Time:"), 3, 2)
        self.end_time_combo = QComboBox()
        self.end_time_combo.setEditable(True)
        self.end_time_combo.addItems([
            "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
            "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM",
            "06:00 PM", "07:00 PM", "08:00 PM"
        ])
        self.end_time_combo.setCurrentText("11:00 AM")
        grid.addWidget(self.end_time_combo, 3, 3)

        # Row 4: Days Schedule & Room / Lab
        grid.addWidget(QLabel("Days Schedule:"), 4, 0)
        self.days_combo = QComboBox()
        self.days_combo.setEditable(True)
        self.days_combo.addItems([
            "Mon-Fri (5 Days)",
            "Mon-Sat (6 Days)",
            "Weekend (Sat-Sun)",
            "Tue-Thu-Sat (Alternate)",
            "Mon-Wed-Fri (Alternate)",
            "Daily / Regular"
        ])
        grid.addWidget(self.days_combo, 4, 1)

        grid.addWidget(QLabel("Room / Lab:"), 4, 2)
        self.room_combo = QComboBox()
        self.room_combo.setEditable(True)
        self.room_combo.addItems([
            "Lab 1 (CAD Station)",
            "Lab 2 (High-End Rendering)",
            "Lab 3 (CNC & Mechanical)",
            "Classroom A (Theory)",
            "Classroom B",
            "Online / Hybrid"
        ])
        grid.addWidget(self.room_combo, 4, 3)

        # Row 5: Max Capacity & Start Date
        grid.addWidget(QLabel("Max Capacity:"), 5, 0)
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 200)
        self.capacity_spin.setValue(20)
        self.capacity_spin.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px;")
        grid.addWidget(self.capacity_spin, 5, 1)

        grid.addWidget(QLabel("Start Date:"), 5, 2)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.start_date_edit.setDate(QDate.currentDate())
        grid.addWidget(self.start_date_edit, 5, 3)

        card_layout.addLayout(grid)

        # Remarks / Syllabus Notes
        card_layout.addWidget(QLabel("Remarks / Syllabus Notes:"))
        self.remarks_input = QTextEdit()
        self.remarks_input.setMaximumHeight(70)
        self.remarks_input.setPlaceholderText("e.g. Covers AutoCAD 2D, 3ds Max Architectural Modeling, V-Ray Rendering, and Photoshop post-production.")
        card_layout.addWidget(self.remarks_input)

        main_layout.addWidget(card)

        # Bottom Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        btn_box.addStretch()

        self.save_btn = QPushButton("💾 Save Batch")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self._on_save)
        btn_box.addWidget(self.save_btn)

        main_layout.addLayout(btn_box)

    def _populate_course_combo(self):
        from app.modules.courses.controllers import CourseController
        self.course_combo.clear()
        self.course_combo.addItem("-- Select Course --", None)
        try:
            courses = CourseController.get_all_courses(status="Active")
            for c in courses:
                self.course_combo.addItem(f"{c.name} (₹{c.standard_fee:,.0f})", c.name)
        except Exception:
            pass

    def _populate_staff_combo(self):
        self.staff_combo.clear()
        self.staff_combo.addItem("-- Unassigned / Open --", None)
        all_staff = StaffController.get_all_staff()
        sel_idx = 0
        for idx, st in enumerate(all_staff, start=1):
            self.staff_combo.addItem(f"{st.name} ({st.designation})", st.id)
            if self.preselected_staff_id and st.id == self.preselected_staff_id:
                sel_idx = idx

        if sel_idx > 0:
            self.staff_combo.setCurrentIndex(sel_idx)

    def _load_batch_data(self):
        b = self.batch
        if not b:
            return
        self.code_input.setText(b.batch_code or "")
        self.name_input.setText(b.batch_name or "")
        
        if b.course_name:
            matched = False
            for i in range(self.course_combo.count()):
                data_val = self.course_combo.itemData(i)
                if data_val and str(data_val).strip().lower() == b.course_name.strip().lower():
                    self.course_combo.setCurrentIndex(i)
                    matched = True
                    break
            if not matched:
                self.course_combo.setEditText(b.course_name)

        # Select staff
        if b.staff_id:
            for i in range(self.staff_combo.count()):
                if self.staff_combo.itemData(i) == b.staff_id:
                    self.staff_combo.setCurrentIndex(i)
                    break

        self.start_time_combo.setCurrentText(b.start_time or "09:00 AM")
        self.end_time_combo.setCurrentText(b.end_time or "11:00 AM")
        self.days_combo.setCurrentText(b.days_schedule or "Mon-Fri")
        self.room_combo.setCurrentText(b.room_lab or "Lab 1")
        self.capacity_spin.setValue(b.max_capacity or 20)

        st_idx = self.status_combo.findText(b.status or "Active")
        if st_idx >= 0:
            self.status_combo.setCurrentIndex(st_idx)

        if b.start_date:
            self.start_date_edit.setDate(QDate(b.start_date.year, b.start_date.month, b.start_date.day))

        self.remarks_input.setPlainText(b.remarks or "")

    def _on_save(self):
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()

        if not code:
            QMessageBox.warning(self, "Validation Error", "Please enter a unique Batch Code.")
            self.code_input.setFocus()
            return

        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter the Batch Title / Name.")
            self.name_input.setFocus()
            return

        # Course name parsing
        course_text = self.course_combo.currentText().strip()
        if course_text.startswith("--"):
            course_name_val = None
        else:
            course_name_val = course_text.split(" (")[0].strip() or None

        q_date = self.start_date_edit.date()
        s_date = date(q_date.year(), q_date.month(), q_date.day())
        staff_id = self.staff_combo.currentData()

        data = {
            "batch_code": code,
            "batch_name": name,
            "course_name": course_name_val,
            "staff_id": staff_id,
            "start_time": self.start_time_combo.currentText().strip(),
            "end_time": self.end_time_combo.currentText().strip(),
            "days_schedule": self.days_combo.currentText().strip(),
            "room_lab": self.room_combo.currentText().strip(),
            "max_capacity": self.capacity_spin.value(),
            "status": self.status_combo.currentText(),
            "start_date": s_date,
            "remarks": self.remarks_input.toPlainText().strip() or None,
        }

        try:
            if self.is_edit_mode and self.batch:
                StaffController.update_batch(self.batch.id, data)
            else:
                StaffController.create_batch(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save batch schedule: {e}")
