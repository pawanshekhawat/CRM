import os
import shutil
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.config import PHOTOS_DIR
from app.models.staff import Staff
from app.modules.staff.controllers import StaffController

class StaffFormDialog(QDialog):
    """Dialog to create or edit a Staff member / Faculty record."""

    def __init__(self, staff: Optional[Staff] = None, parent=None):
        super().__init__(parent)
        self.staff = staff
        self.is_edit_mode = staff is not None
        self.selected_photo_path: Optional[str] = staff.photo_path if staff else None

        self.setWindowTitle("Edit Staff Member" if self.is_edit_mode else "➕ Add New Staff Member")
        self.setMinimumSize(680, 620)
        self.resize(740, 680)

        self._build_ui()
        if self.is_edit_mode:
            self._load_staff_data()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Scroll Area for Form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # 1. Header Card (ID + Photo)
        top_card = QFrame()
        top_card.setObjectName("card")
        top_card_layout = QHBoxLayout(top_card)
        top_card_layout.setContentsMargins(20, 16, 20, 16)
        top_card_layout.setSpacing(20)

        # Left Photo Preview & Upload
        photo_box = QVBoxLayout()
        photo_box.setAlignment(Qt.AlignCenter)
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(90, 110)
        self.photo_preview.setStyleSheet("""
            QLabel {
                background-color: #101520;
                border: 2px dashed #283347;
                border-radius: 8px;
                color: #64748B;
            }
        """)
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setText("No Photo")
        photo_box.addWidget(self.photo_preview)

        btn_row = QHBoxLayout()
        self.upload_photo_btn = QPushButton("📷 Upload")
        self.upload_photo_btn.setStyleSheet("padding: 4px 8px; font-size: 11px;")
        self.upload_photo_btn.clicked.connect(self._on_upload_photo)
        btn_row.addWidget(self.upload_photo_btn)

        self.clear_photo_btn = QPushButton("✕")
        self.clear_photo_btn.setStyleSheet("padding: 4px 6px; font-size: 11px; background: #EF444422; color: #EF4444;")
        self.clear_photo_btn.clicked.connect(self._on_clear_photo)
        btn_row.addWidget(self.clear_photo_btn)
        photo_box.addLayout(btn_row)

        top_card_layout.addLayout(photo_box)

        # Right Top Meta (Staff ID, Status)
        meta_grid = QGridLayout()
        meta_grid.setHorizontalSpacing(14)
        meta_grid.setVerticalSpacing(10)

        meta_grid.addWidget(QLabel("Staff / Employee ID:"), 0, 0)
        self.staff_id_input = QLineEdit()
        if not self.is_edit_mode:
            self.staff_id_input.setText(StaffController.generate_next_staff_id())
        self.staff_id_input.setPlaceholderText("e.g. STF-001")
        meta_grid.addWidget(self.staff_id_input, 0, 1)

        meta_grid.addWidget(QLabel("Status:"), 1, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "On Leave", "Inactive", "Resigned"])
        meta_grid.addWidget(self.status_combo, 1, 1)

        meta_grid.addWidget(QLabel("Joining Date:"), 2, 0)
        self.joining_date_edit = QDateEdit()
        self.joining_date_edit.setCalendarPopup(True)
        self.joining_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.joining_date_edit.setDate(QDate.currentDate())
        meta_grid.addWidget(self.joining_date_edit, 2, 1)

        top_card_layout.addLayout(meta_grid)
        top_card_layout.setStretch(1, 1)
        content_layout.addWidget(top_card)

        # 2. Personal & Professional Details Card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        sec_title = QLabel("👤 Personal & Professional Information")
        sec_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #F1F5F9;")
        card_layout.addWidget(sec_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        # Row 0: Name & Mobile
        grid.addWidget(QLabel("Full Name: *"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Er. Rajesh Sharma")
        grid.addWidget(self.name_input, 0, 1)

        grid.addWidget(QLabel("Mobile No: *"), 0, 2)
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("e.g. 9876543210")
        grid.addWidget(self.mobile_input, 0, 3)

        # Row 1: Designation & Department
        grid.addWidget(QLabel("Designation / Role: *"), 1, 0)
        self.designation_input = QLineEdit()
        self.designation_input.setPlaceholderText("e.g. Senior Architecture Faculty")
        grid.addWidget(self.designation_input, 1, 1)

        grid.addWidget(QLabel("Department:"), 1, 2)
        self.dept_combo = QComboBox()
        self.dept_combo.setEditable(True)
        self.dept_combo.addItems([
            "Civil / Architecture",
            "Mechanical / CAD",
            "IT / Full Stack",
            "Interior Design",
            "Management / Admin",
            "Counseling / Front Desk"
        ])
        grid.addWidget(self.dept_combo, 1, 3)

        # Row 2: Email & Qualification
        grid.addWidget(QLabel("Email Address:"), 2, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. rajesh.caddesk@gmail.com")
        grid.addWidget(self.email_input, 2, 1)

        grid.addWidget(QLabel("Qualification:"), 2, 2)
        self.qualification_input = QLineEdit()
        self.qualification_input.setPlaceholderText("e.g. B.Tech (Civil), Autodesk Certified")
        grid.addWidget(self.qualification_input, 2, 3)

        # Row 3: Monthly Salary
        grid.addWidget(QLabel("Monthly Salary (₹):"), 3, 0)
        self.salary_spin = QDoubleSpinBox()
        self.salary_spin.setRange(0, 10000000)
        self.salary_spin.setDecimals(2)
        self.salary_spin.setSingleStep(1000)
        self.salary_spin.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px;")
        grid.addWidget(self.salary_spin, 3, 1)

        card_layout.addLayout(grid)

        # Notes / Remarks
        card_layout.addWidget(QLabel("Additional Notes / Remarks:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("e.g. Primary instructor for 3ds Max, Revit & AutoCAD batches.")
        card_layout.addWidget(self.notes_input)

        content_layout.addWidget(card)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Bottom Action Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        btn_box.addStretch()

        self.save_btn = QPushButton("💾 Save Staff Member")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self._on_save)
        btn_box.addWidget(self.save_btn)

        main_layout.addLayout(btn_box)

    def _on_upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Staff Passport Photo", "", "Image Files (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file_path:
            PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
            ext = Path(file_path).suffix
            dest_filename = f"staff_{uuid.uuid4().hex[:12]}{ext}"
            dest_path = PHOTOS_DIR / dest_filename
            shutil.copy2(file_path, str(dest_path))
            self.selected_photo_path = dest_filename
            self._update_photo_preview()

    def _on_clear_photo(self):
        self.selected_photo_path = None
        self._update_photo_preview()

    def _update_photo_preview(self):
        if self.selected_photo_path:
            p_path = PHOTOS_DIR / self.selected_photo_path
            if p_path.exists():
                pix = QPixmap(str(p_path)).scaled(90, 110, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.photo_preview.setPixmap(pix)
                self.photo_preview.setText("")
                return
        self.photo_preview.setPixmap(QPixmap())
        self.photo_preview.setText("No Photo")

    def _load_staff_data(self):
        s = self.staff
        if not s:
            return
        self.staff_id_input.setText(s.staff_id or "")
        self.name_input.setText(s.name or "")
        self.mobile_input.setText(s.mobile_no or "")
        self.designation_input.setText(s.designation or "")
        
        dept_idx = self.dept_combo.findText(s.department or "")
        if dept_idx >= 0:
            self.dept_combo.setCurrentIndex(dept_idx)
        else:
            self.dept_combo.setEditText(s.department or "")

        self.email_input.setText(s.email or "")
        self.qualification_input.setText(s.qualification or "")
        self.salary_spin.setValue(s.salary or 0.0)

        st_idx = self.status_combo.findText(s.status or "Active")
        if st_idx >= 0:
            self.status_combo.setCurrentIndex(st_idx)

        if s.joining_date:
            self.joining_date_edit.setDate(QDate(s.joining_date.year, s.joining_date.month, s.joining_date.day))

        self.notes_input.setPlainText(s.notes or "")
        self.selected_photo_path = s.photo_path
        self._update_photo_preview()

    def _on_save(self):
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip() or None
        designation = self.designation_input.text().strip() or None
        staff_id = self.staff_id_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter the Staff Member's Full Name.")
            self.name_input.setFocus()
            return

        q_date = self.joining_date_edit.date()
        j_date = date(q_date.year(), q_date.month(), q_date.day())

        data = {
            "staff_id": staff_id,
            "name": name,
            "mobile_no": mobile,
            "designation": designation,
            "department": self.dept_combo.currentText().strip() or None,
            "email": self.email_input.text().strip() or None,
            "qualification": self.qualification_input.text().strip() or None,
            "salary": self.salary_spin.value(),
            "status": self.status_combo.currentText(),
            "joining_date": j_date,
            "photo_path": self.selected_photo_path,
            "notes": self.notes_input.toPlainText().strip() or None,
        }

        try:
            if self.is_edit_mode and self.staff:
                StaffController.update_staff(self.staff.id, data)
            else:
                StaffController.create_staff(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save staff record: {e}")
