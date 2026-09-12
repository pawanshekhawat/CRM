from typing import Any, Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.models.course import Course
from app.modules.courses.controllers import CourseController

class CourseFormDialog(QDialog):
    """Dialog to create or edit a Course Program in the catalog."""

    def __init__(self, course: Optional[Course] = None, parent=None):
        super().__init__(parent)
        self.course = course
        self.is_edit_mode = course is not None

        self.setWindowTitle("Edit Course Program" if self.is_edit_mode else "➕ Add New Course Program")
        self.setMinimumSize(580, 500)
        self.resize(620, 540)

        self._build_ui()
        if self.is_edit_mode:
            self._load_course_data()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        sec_title = QLabel("🎓 Course Program & Pricing Details")
        sec_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #F1F5F9;")
        card_layout.addWidget(sec_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        # Row 0: Course Code & Status
        grid.addWidget(QLabel("Course Code: *"), 0, 0)
        self.code_input = QLineEdit()
        if not self.is_edit_mode:
            self.code_input.setText(CourseController.generate_next_course_code())
        self.code_input.setPlaceholderText("e.g. CRS-ARCH-01")
        grid.addWidget(self.code_input, 0, 1)

        grid.addWidget(QLabel("Status:"), 0, 2)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Archived"])
        grid.addWidget(self.status_combo, 0, 3)

        # Row 1: Course Name (Full Width)
        grid.addWidget(QLabel("Course Title: *"), 1, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Master in Architecture")
        grid.addWidget(self.name_input, 1, 1, 1, 3)

        # Row 2: Category & Standard Fixed Fee (₹)
        grid.addWidget(QLabel("Department / Category:"), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems([
            "Architecture & Civil",
            "Interior Design",
            "Data & AI",
            "IT & Programming",
            "Civil & Survey",
            "Drafting & CAD",
            "Mechanical & Design",
            "Multimedia & Graphics",
            "Computer Applications",
            "Digital Marketing",
            "Accounting & Finance",
            "Foundational IT",
            "General",
        ])
        grid.addWidget(self.category_combo, 2, 1)

        grid.addWidget(QLabel("Standard Fee (₹): *"), 2, 2)
        self.fee_spin = QDoubleSpinBox()
        self.fee_spin.setRange(0, 10000000)
        self.fee_spin.setDecimals(2)
        self.fee_spin.setSingleStep(500)
        self.fee_spin.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px; font-weight: bold; color: #10B981;")
        grid.addWidget(self.fee_spin, 2, 3)

        card_layout.addLayout(grid)

        # Row 3: Description / Syllabus / Tools Covered
        card_layout.addWidget(QLabel("Syllabus / Software Tools Covered / Summary:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(90)
        self.desc_input.setPlaceholderText("e.g. AutoCAD, Revit Architecture, 3ds Max, V-Ray, Photoshop, BIM workflows.")
        card_layout.addWidget(self.desc_input)

        main_layout.addWidget(card)

        # Bottom Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        btn_box.addStretch()

        self.save_btn = QPushButton("💾 Save Course")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self._on_save)
        btn_box.addWidget(self.save_btn)

        main_layout.addLayout(btn_box)

    def _load_course_data(self):
        c = self.course
        if not c:
            return

        self.code_input.setText(c.course_code or "")
        self.name_input.setText(c.name or "")
        
        c_idx = self.category_combo.findText(c.category or "")
        if c_idx >= 0:
            self.category_combo.setCurrentIndex(c_idx)
        else:
            self.category_combo.setEditText(c.category or "")

        self.fee_spin.setValue(c.standard_fee or 0.0)

        st_idx = self.status_combo.findText(c.status or "Active")
        if st_idx >= 0:
            self.status_combo.setCurrentIndex(st_idx)

        self.desc_input.setPlainText(c.description or "")

    def _on_save(self):
        name = self.name_input.text().strip()
        code = self.code_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter the Course Title / Name.")
            self.name_input.setFocus()
            return

        if not code:
            QMessageBox.warning(self, "Validation Error", "Please provide a Course Code.")
            self.code_input.setFocus()
            return

        data = {
            "course_code": code,
            "name": name,
            "category": self.category_combo.currentText().strip() or "General",
            "standard_fee": self.fee_spin.value(),
            "status": self.status_combo.currentText(),
            "description": self.desc_input.toPlainText().strip() or None,
        }

        try:
            if self.is_edit_mode and self.course:
                CourseController.update_course(self.course.id, data)
            else:
                CourseController.create_course(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save course: {e}")
