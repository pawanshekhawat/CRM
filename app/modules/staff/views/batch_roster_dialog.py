from datetime import date
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
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
    QWidget,
)

from app.core.config import PHOTOS_DIR
from app.models.staff import Batch, BatchStudent
from app.models.student import Student
from app.modules.staff.controllers import StaffController
from app.modules.students.views.student_list_view import create_student_avatar_pixmap

class BatchRosterDialog(QDialog):
    """Dialog to view and manage student enrollments inside a specific Batch."""

    def __init__(self, batch_id: str, parent=None):
        super().__init__(parent)
        self.batch_id = batch_id
        self.batch: Optional[Batch] = None

        self.setWindowTitle("Batch Student Roster & Allocations")
        self.setMinimumSize(850, 620)
        self.resize(900, 680)

        self._build_ui()
        self._reload_roster()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(16)

        # 1. Batch Header Info Card
        self.header_card = QFrame()
        self.header_card.setObjectName("card")
        self.header_layout = QHBoxLayout(self.header_card)
        self.header_layout.setContentsMargins(20, 16, 20, 16)
        self.header_layout.setSpacing(20)

        self.info_box = QVBoxLayout()
        self.batch_title_lbl = QLabel("Batch Title")
        self.batch_title_lbl.setStyleSheet("font-size: 17px; font-weight: 800; color: #F8FAFC;")
        self.info_box.addWidget(self.batch_title_lbl)

        self.batch_meta_lbl = QLabel("Code | Instructor | Timing")
        self.batch_meta_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        self.info_box.addWidget(self.batch_meta_lbl)
        self.header_layout.addLayout(self.info_box)

        self.header_layout.addStretch()

        # Capacity Badge
        self.capacity_badge = QLabel("0 / 20 Enrolled")
        self.capacity_badge.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 700;
                color: #38BDF8;
                background-color: #0284C722;
                border: 1px solid #0284C755;
                border-radius: 8px;
                padding: 6px 14px;
            }
        """)
        self.header_layout.addWidget(self.capacity_badge)

        self.main_layout.addWidget(self.header_card)

        # 2. Add / Enroll Student Bar
        enroll_bar = QFrame()
        enroll_bar.setObjectName("card")
        e_layout = QHBoxLayout(enroll_bar)
        e_layout.setContentsMargins(16, 12, 16, 12)
        e_layout.setSpacing(12)

        e_layout.addWidget(QLabel("<b>➕ Enroll Student:</b>"))

        self.student_combo = QComboBox()
        self.student_combo.setMinimumWidth(320)
        e_layout.addWidget(self.student_combo)

        enroll_btn = QPushButton("Add to Batch Roster")
        enroll_btn.setObjectName("primaryBtn")
        enroll_btn.clicked.connect(self._on_enroll_student)
        e_layout.addWidget(enroll_btn)

        e_layout.addStretch()
        self.main_layout.addWidget(enroll_bar)

        # 3. Enrolled Students Table
        self.table = QTableWidget(0, 7)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setHorizontalHeaderLabels([
            "Avatar", "Student ID", "Student Name", "Mobile No", "Course", "Enrolled Date", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        self.main_layout.addWidget(self.table)

        # 4. Bottom Close Button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        self.main_layout.addLayout(btn_box)

    def _reload_roster(self):
        self.batch = StaffController.get_batch_by_id(self.batch_id)
        if not self.batch:
            return

        b = self.batch
        self.batch_title_lbl.setText(f"{b.batch_name} ({b.batch_code})")
        instructor_str = f"Instructor: {b.instructor.name}" if b.instructor else "Instructor: Unassigned"
        schedule_str = f"{b.start_time} - {b.end_time} ({b.days_schedule or 'Regular'}) • {b.room_lab or 'Lab'}"
        self.batch_meta_lbl.setText(f"Course: {b.course_name or 'N/A'} | {instructor_str} | {schedule_str}")

        enrollments = b.enrollments or []
        active_count = len(enrollments)
        self.capacity_badge.setText(f"👥 {active_count} / {b.max_capacity} Enrolled")

        # Repopulate Student Combo with available active students
        self.student_combo.clear()
        available_students = StaffController.get_unassigned_students_for_batch(self.batch_id)
        if available_students:
            self.student_combo.addItem("-- Select Student to Enroll --", None)
            for s in available_students:
                self.student_combo.addItem(f"{s.name} ({s.id_no} - {s.course_name or 'N/A'})", s.id)
        else:
            self.student_combo.addItem("All active students are already enrolled", None)

        # Populate Table
        self.table.setRowCount(0)
        for row_idx, enr in enumerate(enrollments):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 46)

            st: Student = enr.student

            # 0. Avatar
            avatar_lbl = QLabel()
            avatar_lbl.setAlignment(Qt.AlignCenter)
            if st and st.photo_path:
                p_path = PHOTOS_DIR / st.photo_path
                if p_path.exists():
                    pix = QPixmap(str(p_path)).scaled(32, 32, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    avatar_lbl.setPixmap(pix)
                else:
                    avatar_lbl.setPixmap(create_student_avatar_pixmap(None, st.name, size=32))
            else:
                avatar_lbl.setPixmap(create_student_avatar_pixmap(None, st.name if st else "U", size=32))
            self.table.setCellWidget(row_idx, 0, avatar_lbl)

            # 1. Student ID
            id_item = QTableWidgetItem(st.id_no if st else "N/A")
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, id_item)

            # 2. Student Name
            name_item = QTableWidgetItem(f" {st.name if st else 'Unknown'} ")
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            self.table.setItem(row_idx, 2, name_item)

            # 3. Mobile No
            mob_item = QTableWidgetItem(st.mobile_no if st else "-")
            mob_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, mob_item)

            # 4. Course
            course_item = QTableWidgetItem(st.course_name or "-")
            self.table.setItem(row_idx, 4, course_item)

            # 5. Enrolled Date
            dt_item = QTableWidgetItem(enr.enrolled_date.strftime("%d/%m/%Y") if enr.enrolled_date else "-")
            dt_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, dt_item)

            # 6. Action: Remove Button
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setAlignment(Qt.AlignCenter)

            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("background-color: #EF444422; color: #EF4444; border: 1px solid #EF444455; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
            student_id_val = st.id if st else enr.student_id
            remove_btn.clicked.connect(lambda _, s_id=student_id_val: self._on_remove_student(s_id))
            a_layout.addWidget(remove_btn)

            self.table.setCellWidget(row_idx, 6, action_widget)

    def _on_enroll_student(self):
        student_id = self.student_combo.currentData()
        if not student_id:
            QMessageBox.information(self, "Select Student", "Please select a valid student from the dropdown list.")
            return

        try:
            StaffController.enroll_student_in_batch(self.batch_id, student_id)
            self._reload_roster()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to enroll student into batch: {e}")

    def _on_remove_student(self, student_id: str):
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove this student from the batch?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                StaffController.remove_student_from_batch(self.batch_id, student_id)
                self._reload_roster()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove student from batch: {e}")
