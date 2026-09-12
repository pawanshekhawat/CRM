from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.config import PHOTOS_DIR
from app.models.staff import Batch, Staff
from app.models.student import Student
from app.modules.staff.controllers import StaffController
from app.modules.staff.views.batch_form_dialog import BatchFormDialog
from app.modules.staff.views.batch_roster_dialog import BatchRosterDialog
from app.modules.staff.views.staff_form_dialog import StaffFormDialog
from app.modules.students.views.student_list_view import create_student_avatar_pixmap

class StaffDetailDialog(QDialog):
    """Detailed Profile View for a Staff Member with Batches & Student Allocations."""

    staff_updated = Signal()

    def __init__(self, staff_id: str, parent=None):
        super().__init__(parent)
        self.staff_id = staff_id
        self.staff: Optional[Staff] = None

        self.setWindowTitle("Staff Profile & Batch Allocations")
        self.setMinimumSize(920, 680)
        self.resize(980, 720)

        self._load_staff_data()
        self._build_ui()

    def _load_staff_data(self):
        self.staff = StaffController.get_staff_by_id(self.staff_id)

    def _build_ui(self):
        # Clear layout if rebuilding
        if self.layout():
            QWidget().setLayout(self.layout())

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(16)

        s = self.staff
        if not s:
            self.main_layout.addWidget(QLabel("Staff record not found."))
            return

        # 1. Top Header Profile Banner
        header_card = QFrame()
        header_card.setObjectName("card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(20)

        # Photo Avatar
        photo_lbl = QLabel()
        photo_lbl.setFixedSize(80, 96)
        photo_lbl.setAlignment(Qt.AlignCenter)
        if s.photo_path:
            p_path = PHOTOS_DIR / s.photo_path
            if p_path.exists():
                pix = QPixmap(str(p_path)).scaled(80, 96, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                photo_lbl.setPixmap(pix)
            else:
                photo_lbl.setPixmap(create_student_avatar_pixmap(None, s.name, size=80))
        else:
            photo_lbl.setPixmap(create_student_avatar_pixmap(None, s.name, size=80))
        h_layout.addWidget(photo_lbl)

        # Name & Info
        info_box = QVBoxLayout()
        name_lbl = QLabel(s.name)
        name_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #F8FAFC;")
        info_box.addWidget(name_lbl)

        sub_info = QLabel(f"<b>ID:</b> {s.staff_id} | <b>Designation:</b> {s.designation or '-'} | <b>Department:</b> {s.department or '-'} | <b>Mobile:</b> {s.mobile_no or '-'}")
        sub_info.setStyleSheet("font-size: 12px; color: #94A3B8;")
        info_box.addWidget(sub_info)

        # Badges Row
        badge_row = QHBoxLayout()
        badge_row.setSpacing(10)

        st_color = "#10B981" if s.status == "Active" else ("#F59E0B" if s.status == "On Leave" else "#EF4444")
        st_badge = QLabel(f" {s.status} ")
        st_badge.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {st_color}; background-color: {st_color}22; border: 1px solid {st_color}55; border-radius: 6px; padding: 2px 8px;")
        badge_row.addWidget(st_badge)

        batches_count = len(s.batches or [])
        b_badge = QLabel(f" 📚 {batches_count} Batches ")
        b_badge.setStyleSheet("font-size: 11px; font-weight: bold; color: #38BDF8; background-color: #38BDF822; border: 1px solid #38BDF855; border-radius: 6px; padding: 2px 8px;")
        badge_row.addWidget(b_badge)

        students_count = s.total_students_count
        std_badge = QLabel(f" 👥 {students_count} Total Students ")
        std_badge.setStyleSheet("font-size: 11px; font-weight: bold; color: #A855F7; background-color: #A855F722; border: 1px solid #A855F755; border-radius: 6px; padding: 2px 8px;")
        badge_row.addWidget(std_badge)

        badge_row.addStretch()
        info_box.addLayout(badge_row)
        h_layout.addLayout(info_box)

        h_layout.addStretch()

        # Edit Profile Button
        edit_btn = QPushButton("✏️ Edit Staff Details")
        edit_btn.clicked.connect(self._on_edit)
        h_layout.addWidget(edit_btn)

        self.main_layout.addWidget(header_card)

        # 2. Main Tabbed Content Area
        tabs = QTabWidget()

        # Tab 1: Personal & Professional Details
        overview_tab = QWidget()
        ov_layout = QVBoxLayout(overview_tab)
        ov_layout.setContentsMargins(16, 16, 16, 16)

        ov_grid = QGridLayout()
        ov_grid.setHorizontalSpacing(24)
        ov_grid.setVerticalSpacing(14)

        details = [
            ("Staff ID / Code:", s.staff_id),
            ("Full Name:", s.name),
            ("Designation / Role:", s.designation or "-"),
            ("Department:", s.department or "-"),
            ("Primary Mobile:", s.mobile_no or "-"),
            ("Email Address:", s.email or "N/A"),
            ("Qualification:", s.qualification or "N/A"),
            ("Joining Date:", s.joining_date.strftime("%d/%m/%Y") if s.joining_date else "N/A"),
            ("Monthly Salary / Pay:", f"₹{s.salary:,.2f}" if s.salary else "N/A"),
            ("Status:", s.status),
        ]

        row, col = 0, 0
        for label_text, val_text in details:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: 600; color: #94A3B8; font-size: 13px;")
            val = QLabel(str(val_text))
            val.setStyleSheet("color: #F1F5F9; font-weight: 500; font-size: 13px;")

            ov_grid.addWidget(lbl, row, col * 2)
            ov_grid.addWidget(val, row, col * 2 + 1)

            col += 1
            if col >= 2:
                col = 0
                row += 1

        ov_layout.addLayout(ov_grid)
        ov_layout.addSpacing(14)

        if s.notes:
            ov_layout.addWidget(QLabel("<b>Notes & Remarks:</b>"))
            notes_lbl = QLabel(s.notes)
            notes_lbl.setStyleSheet("color: #CBD5E1; background-color: #121824; border: 1px solid #1E293B; border-radius: 6px; padding: 8px;")
            notes_lbl.setWordWrap(True)
            ov_layout.addWidget(notes_lbl)

        ov_layout.addStretch()
        tabs.addTab(overview_tab, "📋 Profile & Details")

        # Tab 2: Conducted Batches
        batches_tab = QWidget()
        b_layout = QVBoxLayout(batches_tab)
        b_layout.setContentsMargins(16, 16, 16, 16)
        b_layout.setSpacing(12)

        # Top Bar for Batches Tab
        b_top = QHBoxLayout()
        b_title = QLabel(f"<b>Active & Scheduled Batches ({len(s.batches or [])}):</b>")
        b_top.addWidget(b_title)
        b_top.addStretch()

        add_batch_btn = QPushButton("➕ Create New Batch for this Faculty")
        add_batch_btn.setObjectName("primaryBtn")
        add_batch_btn.clicked.connect(self._on_add_batch_for_staff)
        b_top.addWidget(add_batch_btn)
        b_layout.addLayout(b_top)

        # Batches Table
        batch_table = QTableWidget(0, 7)
        batch_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        batch_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        batch_table.setHorizontalHeaderLabels([
            "Batch Code", "Batch Title", "Course", "Timing & Schedule", "Room", "Enrolled / Cap", "Action"
        ])
        batch_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        batch_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        batch_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        batch_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        batch_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        batch_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        batch_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        batch_table.verticalHeader().setVisible(False)

        for b_idx, b in enumerate(s.batches or []):
            batch_table.insertRow(b_idx)
            batch_table.setRowHeight(b_idx, 44)

            # Code
            c_item = QTableWidgetItem(b.batch_code)
            c_item.setTextAlignment(Qt.AlignCenter)
            batch_table.setItem(b_idx, 0, c_item)

            # Title
            t_item = QTableWidgetItem(f" {b.batch_name} ")
            f = QFont()
            f.setBold(True)
            t_item.setFont(f)
            batch_table.setItem(b_idx, 1, t_item)

            # Course
            batch_table.setItem(b_idx, 2, QTableWidgetItem(b.course_name or "-"))

            # Timing & Schedule
            sched_str = f"{b.start_time or ''} - {b.end_time or ''} ({b.days_schedule or 'Mon-Fri'})"
            batch_table.setItem(b_idx, 3, QTableWidgetItem(sched_str))

            # Room
            batch_table.setItem(b_idx, 4, QTableWidgetItem(b.room_lab or "-"))

            # Capacity
            enr_count = b.enrolled_count
            cap_item = QTableWidgetItem(f"{enr_count} / {b.max_capacity}")
            cap_item.setTextAlignment(Qt.AlignCenter)
            batch_table.setItem(b_idx, 5, cap_item)

            # Action: Manage Roster
            roster_btn = QPushButton("👥 Manage Roster")
            roster_btn.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            roster_btn.clicked.connect(lambda _, b_id=b.id: self._open_batch_roster(b_id))
            batch_table.setCellWidget(b_idx, 6, roster_btn)

        b_layout.addWidget(batch_table)
        tabs.addTab(batches_tab, f"📚 Conducted Batches ({len(s.batches or [])})")

        # Tab 3: Assigned Students Roster
        students_tab = QWidget()
        std_layout = QVBoxLayout(students_tab)
        std_layout.setContentsMargins(16, 16, 16, 16)

        std_layout.addWidget(QLabel("<b>All Students Mentored or Enrolled across Batches:</b>"))

        std_table = QTableWidget(0, 6)
        std_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        std_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        std_table.setHorizontalHeaderLabels([
            "Avatar", "Student ID", "Student Name", "Mobile No", "Course", "Enrolled Batch(es)"
        ])
        std_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        std_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        std_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        std_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        std_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        std_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        std_table.verticalHeader().setVisible(False)

        # Collect unique students and their associated batches
        student_map = {}
        # Direct mentees
        for st in (s.assigned_students or []):
            student_map[st.id] = (st, ["Direct Mentorship"])

        # Batch students
        for b in (s.batches or []):
            for enr in (b.enrollments or []):
                st = enr.student
                if st:
                    if st.id not in student_map:
                        student_map[st.id] = (st, [b.batch_code])
                    else:
                        if b.batch_code not in student_map[st.id][1]:
                            student_map[st.id][1].append(b.batch_code)

        for row_i, (st_id, (st, b_codes)) in enumerate(student_map.items()):
            std_table.insertRow(row_i)
            std_table.setRowHeight(row_i, 44)

            # Avatar
            avatar_lbl = QLabel()
            avatar_lbl.setAlignment(Qt.AlignCenter)
            if st.photo_path:
                p_path = PHOTOS_DIR / st.photo_path
                if p_path.exists():
                    pix = QPixmap(str(p_path)).scaled(30, 30, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    avatar_lbl.setPixmap(pix)
                else:
                    avatar_lbl.setPixmap(create_student_avatar_pixmap(None, st.name, size=30))
            else:
                avatar_lbl.setPixmap(create_student_avatar_pixmap(None, st.name, size=30))
            std_table.setCellWidget(row_i, 0, avatar_lbl)

            # ID
            id_itm = QTableWidgetItem(st.id_no)
            id_itm.setTextAlignment(Qt.AlignCenter)
            std_table.setItem(row_i, 1, id_itm)

            # Name
            name_itm = QTableWidgetItem(f" {st.name} ")
            f = QFont()
            f.setBold(True)
            name_itm.setFont(f)
            std_table.setItem(row_i, 2, name_itm)

            # Mobile
            mob_itm = QTableWidgetItem(st.mobile_no or "-")
            mob_itm.setTextAlignment(Qt.AlignCenter)
            std_table.setItem(row_i, 3, mob_itm)

            # Course
            std_table.setItem(row_i, 4, QTableWidgetItem(st.course_name or "-"))

            # Enrolled Batches
            batches_str = ", ".join(b_codes)
            std_table.setItem(row_i, 5, QTableWidgetItem(batches_str))

        std_layout.addWidget(std_table)
        tabs.addTab(students_tab, f"👥 Assigned Students ({len(student_map)})")

        self.main_layout.addWidget(tabs)

        # Bottom Actions Bar
        b_row = QHBoxLayout()
        del_btn = QPushButton("🗑️ Delete Staff Record")
        del_btn.setObjectName("dangerBtn")
        del_btn.clicked.connect(self._on_delete)
        b_row.addWidget(del_btn)

        b_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        b_row.addWidget(close_btn)

        self.main_layout.addLayout(b_row)

    def _on_edit(self):
        dlg = StaffFormDialog(staff=self.staff, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._load_staff_data()
            self._build_ui()
            self.staff_updated.emit()

    def _on_add_batch_for_staff(self):
        dlg = BatchFormDialog(preselected_staff_id=self.staff_id, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._load_staff_data()
            self._build_ui()
            self.staff_updated.emit()

    def _open_batch_roster(self, batch_id: str):
        dlg = BatchRosterDialog(batch_id=batch_id, parent=self)
        dlg.exec()
        self._load_staff_data()
        self._build_ui()
        self.staff_updated.emit()

    def _on_delete(self):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete staff member {self.staff.name} ({self.staff.staff_id})?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            StaffController.delete_staff(self.staff.id)
            self.staff_updated.emit()
            self.accept()
