from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
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
from app.modules.staff.controllers import StaffController
from app.modules.staff.views.batch_form_dialog import BatchFormDialog
from app.modules.staff.views.batch_roster_dialog import BatchRosterDialog
from app.modules.staff.views.staff_detail_dialog import StaffDetailDialog
from app.modules.staff.views.staff_form_dialog import StaffFormDialog
from app.modules.students.views.student_list_view import create_student_avatar_pixmap
from app.ui.widgets.stat_card import StatCard

class StaffListView(QWidget):
    """Main Management View for Staff Members, Batches, and Allocations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # 1. Top Header Bar
        top_bar = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        title = QLabel("Staff & Batch Management")
        title.setObjectName("pageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC;")
        header_text.addWidget(title)

        subtitle = QLabel("Faculty directory, batch schedules, classroom allocation, and student rosters.")
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        header_text.addWidget(subtitle)

        top_bar.addLayout(header_text)
        top_bar.addStretch()

        # Action Buttons
        self.add_batch_btn = QPushButton("➕ Create Batch")
        self.add_batch_btn.setStyleSheet("padding: 8px 14px; font-weight: 600;")
        self.add_batch_btn.clicked.connect(self._on_create_batch)
        top_bar.addWidget(self.add_batch_btn)

        self.add_staff_btn = QPushButton("👨‍🏫 Add Staff Member")
        self.add_staff_btn.setObjectName("primaryBtn")
        self.add_staff_btn.clicked.connect(self._on_create_staff)
        top_bar.addWidget(self.add_staff_btn)

        main_layout.addLayout(top_bar)

        # 2. Stat Summary Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        self.card_total_staff = StatCard("Total Staff", "0", "Registered staff", "👨‍🏫", "#3B82F6")
        self.card_active_staff = StatCard("Active Faculty", "0", "Instructors on duty", "✅", "#10B981")
        self.card_total_batches = StatCard("Total Batches", "0", "Active batches", "📚", "#8B5CF6")
        self.card_enrollments = StatCard("Total Enrollments", "0", "Active student seats", "🎓", "#EC4899")

        stats_layout.addWidget(self.card_total_staff)
        stats_layout.addWidget(self.card_active_staff)
        stats_layout.addWidget(self.card_total_batches)
        stats_layout.addWidget(self.card_enrollments)

        main_layout.addLayout(stats_layout)

        # 3. Main Tabs: Staff Directory & Batch Schedules
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                font-size: 13px;
                font-weight: 600;
                padding: 8px 18px;
            }
        """)

        # Tab 1: Staff Directory
        staff_tab = self._build_staff_tab()
        self.tabs.addTab(staff_tab, "👨‍🏫 Staff Directory")

        # Tab 2: Batch Schedules & Rosters
        batch_tab = self._build_batch_tab()
        self.tabs.addTab(batch_tab, "📚 Batch Schedules & Rosters")

        main_layout.addWidget(self.tabs)

    def _build_staff_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        # Filters Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        self.staff_search_input = QLineEdit()
        self.staff_search_input.setPlaceholderText("🔍 Search staff by name, ID, mobile, designation...")
        self.staff_search_input.textChanged.connect(self.reload_staff_table)
        filter_bar.addWidget(self.staff_search_input, stretch=2)

        filter_bar.addWidget(QLabel("Department:"))
        self.staff_dept_filter = QComboBox()
        self.staff_dept_filter.addItems(["All", "Civil / Architecture", "Mechanical / CAD", "IT / Full Stack", "Interior Design", "Management / Admin"])
        self.staff_dept_filter.currentTextChanged.connect(self.reload_staff_table)
        filter_bar.addWidget(self.staff_dept_filter)

        filter_bar.addWidget(QLabel("Status:"))
        self.staff_status_filter = QComboBox()
        self.staff_status_filter.addItems(["All", "Active", "On Leave", "Inactive", "Resigned"])
        self.staff_status_filter.currentTextChanged.connect(self.reload_staff_table)
        filter_bar.addWidget(self.staff_status_filter)

        layout.addLayout(filter_bar)

        # Staff Table
        self.staff_table = QTableWidget(0, 10)
        self.staff_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.staff_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.staff_table.setHorizontalHeaderLabels([
            "Photo", "Staff ID", "Full Name", "Designation", "Department", "Mobile No", "Batches", "Students", "Status", "Actions"
        ])
        self.staff_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.staff_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.staff_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.staff_table.verticalHeader().setVisible(False)

        layout.addWidget(self.staff_table)
        return widget

    def _build_batch_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        # Filters Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        self.batch_search_input = QLineEdit()
        self.batch_search_input.setPlaceholderText("🔍 Search batches by code, title, course, room...")
        self.batch_search_input.textChanged.connect(self.reload_batch_table)
        filter_bar.addWidget(self.batch_search_input, stretch=2)

        filter_bar.addWidget(QLabel("Faculty:"))
        self.batch_faculty_filter = QComboBox()
        self.batch_faculty_filter.addItem("All", "All")
        self.batch_faculty_filter.currentIndexChanged.connect(self.reload_batch_table)
        filter_bar.addWidget(self.batch_faculty_filter)

        filter_bar.addWidget(QLabel("Status:"))
        self.batch_status_filter = QComboBox()
        self.batch_status_filter.addItems(["All", "Active", "Upcoming", "Completed", "Suspended"])
        self.batch_status_filter.currentTextChanged.connect(self.reload_batch_table)
        filter_bar.addWidget(self.batch_status_filter)

        layout.addLayout(filter_bar)

        # Batch Table
        self.batch_table = QTableWidget(0, 9)
        self.batch_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.batch_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.batch_table.setHorizontalHeaderLabels([
            "Batch Code", "Batch Title", "Course", "Assigned Faculty", "Schedule & Time", "Room", "Enrolled", "Status", "Actions"
        ])
        self.batch_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.batch_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.batch_table.verticalHeader().setVisible(False)

        layout.addWidget(self.batch_table)
        return widget

    def reload_data(self):
        """Refreshes metrics, staff list, and batches list."""
        metrics = StaffController.get_staff_dashboard_metrics()
        self.card_total_staff.set_value(str(metrics["total_staff"]))
        self.card_active_staff.set_value(str(metrics["active_staff"]))
        self.card_total_batches.set_value(str(metrics["active_batches"]))
        self.card_enrollments.set_value(str(metrics["active_enrollments"]))

        # Update faculty filter combo in batches tab
        current_data = self.batch_faculty_filter.currentData()
        self.batch_faculty_filter.blockSignals(True)
        self.batch_faculty_filter.clear()
        self.batch_faculty_filter.addItem("All", "All")
        all_staff = StaffController.get_all_staff()
        for s in all_staff:
            self.batch_faculty_filter.addItem(s.name, s.id)
        
        # Restore selection
        idx = self.batch_faculty_filter.findData(current_data)
        if idx >= 0:
            self.batch_faculty_filter.setCurrentIndex(idx)
        self.batch_faculty_filter.blockSignals(False)

        self.reload_staff_table()
        self.reload_batch_table()

    def reload_staff_table(self):
        search = self.staff_search_input.text().strip() or None
        dept = self.staff_dept_filter.currentText()
        st = self.staff_status_filter.currentText()

        staff_list = StaffController.get_all_staff(search=search, department=dept, status=st)
        self.staff_table.setRowCount(0)

        for row_idx, s in enumerate(staff_list):
            self.staff_table.insertRow(row_idx)
            self.staff_table.setRowHeight(row_idx, 46)

            # 0. Photo Avatar
            avatar_lbl = QLabel()
            avatar_lbl.setAlignment(Qt.AlignCenter)
            if s.photo_path:
                p_path = PHOTOS_DIR / s.photo_path
                if p_path.exists():
                    pix = QPixmap(str(p_path)).scaled(32, 32, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    avatar_lbl.setPixmap(pix)
                else:
                    avatar_lbl.setPixmap(create_student_avatar_pixmap(None, s.name, size=32))
            else:
                avatar_lbl.setPixmap(create_student_avatar_pixmap(None, s.name, size=32))
            self.staff_table.setCellWidget(row_idx, 0, avatar_lbl)

            # 1. Staff ID
            id_item = QTableWidgetItem(s.staff_id)
            id_item.setTextAlignment(Qt.AlignCenter)
            self.staff_table.setItem(row_idx, 1, id_item)

            # 2. Name
            name_item = QTableWidgetItem(f" {s.name} ")
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            self.staff_table.setItem(row_idx, 2, name_item)

            # 3. Designation
            self.staff_table.setItem(row_idx, 3, QTableWidgetItem(s.designation or "-"))

            # 4. Department
            self.staff_table.setItem(row_idx, 4, QTableWidgetItem(s.department or "-"))

            # 5. Mobile
            mob_item = QTableWidgetItem(s.mobile_no or "-")
            mob_item.setTextAlignment(Qt.AlignCenter)
            self.staff_table.setItem(row_idx, 5, mob_item)

            # 6. Batches Count
            b_count = len(s.batches or [])
            b_item = QTableWidgetItem(str(b_count))
            b_item.setTextAlignment(Qt.AlignCenter)
            self.staff_table.setItem(row_idx, 6, b_item)

            # 7. Students Count
            std_count = s.total_students_count
            std_item = QTableWidgetItem(str(std_count))
            std_item.setTextAlignment(Qt.AlignCenter)
            self.staff_table.setItem(row_idx, 7, std_item)

            # 8. Status Badge
            st_color = "#10B981" if s.status == "Active" else ("#F59E0B" if s.status == "On Leave" else "#EF4444")
            st_badge = QLabel(f" {s.status} ")
            st_badge.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {st_color}; background-color: {st_color}22; border: 1px solid {st_color}55; border-radius: 6px; padding: 2px 6px;")
            st_badge.setAlignment(Qt.AlignCenter)
            self.staff_table.setCellWidget(row_idx, 8, st_badge)

            # 9. Actions
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setSpacing(6)
            a_layout.setAlignment(Qt.AlignCenter)

            view_btn = QPushButton("👁️ Profile")
            view_btn.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            view_btn.clicked.connect(lambda _, st_id=s.id: self._open_staff_profile(st_id))
            a_layout.addWidget(view_btn)

            edit_btn = QPushButton("✏️")
            edit_btn.setStyleSheet("padding: 4px 6px; font-size: 11px;")
            edit_btn.clicked.connect(lambda _, st_id=s.id: self._edit_staff(st_id))
            a_layout.addWidget(edit_btn)

            self.staff_table.setCellWidget(row_idx, 9, action_widget)

    def reload_batch_table(self):
        search = self.batch_search_input.text().strip() or None
        faculty_id = self.batch_faculty_filter.currentData()
        st = self.batch_status_filter.currentText()

        batch_list = StaffController.get_all_batches(staff_id=faculty_id, status=st, search=search)
        self.batch_table.setRowCount(0)

        for row_idx, b in enumerate(batch_list):
            self.batch_table.insertRow(row_idx)
            self.batch_table.setRowHeight(row_idx, 46)

            # 0. Batch Code
            code_item = QTableWidgetItem(b.batch_code)
            code_item.setTextAlignment(Qt.AlignCenter)
            self.batch_table.setItem(row_idx, 0, code_item)

            # 1. Batch Title
            name_item = QTableWidgetItem(f" {b.batch_name} ")
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            self.batch_table.setItem(row_idx, 1, name_item)

            # 2. Course
            self.batch_table.setItem(row_idx, 2, QTableWidgetItem(b.course_name or "-"))

            # 3. Faculty
            fac_name = b.instructor.name if b.instructor else "Unassigned"
            self.batch_table.setItem(row_idx, 3, QTableWidgetItem(fac_name))

            # 4. Schedule & Time
            sched_str = f"{b.start_time or ''} - {b.end_time or ''} ({b.days_schedule or 'Mon-Fri'})"
            self.batch_table.setItem(row_idx, 4, QTableWidgetItem(sched_str))

            # 5. Room
            self.batch_table.setItem(row_idx, 5, QTableWidgetItem(b.room_lab or "-"))

            # 6. Capacity
            enr_count = b.enrolled_count
            cap_item = QTableWidgetItem(f"{enr_count} / {b.max_capacity}")
            cap_item.setTextAlignment(Qt.AlignCenter)
            self.batch_table.setItem(row_idx, 6, cap_item)

            # 7. Status Badge
            st_color = "#10B981" if b.status == "Active" else ("#38BDF8" if b.status == "Upcoming" else "#64748B")
            st_badge = QLabel(f" {b.status} ")
            st_badge.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {st_color}; background-color: {st_color}22; border: 1px solid {st_color}55; border-radius: 6px; padding: 2px 6px;")
            st_badge.setAlignment(Qt.AlignCenter)
            self.batch_table.setCellWidget(row_idx, 7, st_badge)

            # 8. Actions
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setSpacing(6)
            a_layout.setAlignment(Qt.AlignCenter)

            roster_btn = QPushButton("👥 Roster")
            roster_btn.setStyleSheet("padding: 4px 8px; font-size: 11px; background-color: #2563EB22; color: #60A5FA; border: 1px solid #2563EB55;")
            roster_btn.clicked.connect(lambda _, b_id=b.id: self._open_batch_roster(b_id))
            a_layout.addWidget(roster_btn)

            edit_btn = QPushButton("✏️")
            edit_btn.setStyleSheet("padding: 4px 6px; font-size: 11px;")
            edit_btn.clicked.connect(lambda _, b_id=b.id: self._edit_batch(b_id))
            a_layout.addWidget(edit_btn)

            self.batch_table.setCellWidget(row_idx, 8, action_widget)

    def _on_create_staff(self):
        dlg = StaffFormDialog(parent=self)
        if dlg.exec() == StaffFormDialog.Accepted:
            self.reload_data()

    def _edit_staff(self, staff_id: str):
        staff = StaffController.get_staff_by_id(staff_id)
        if staff:
            dlg = StaffFormDialog(staff=staff, parent=self)
            if dlg.exec() == StaffFormDialog.Accepted:
                self.reload_data()

    def _open_staff_profile(self, staff_id: str):
        dlg = StaffDetailDialog(staff_id=staff_id, parent=self)
        dlg.staff_updated.connect(self.reload_data)
        dlg.exec()

    def _on_create_batch(self):
        dlg = BatchFormDialog(parent=self)
        if dlg.exec() == BatchFormDialog.Accepted:
            self.reload_data()

    def _edit_batch(self, batch_id: str):
        batch = StaffController.get_batch_by_id(batch_id)
        if batch:
            dlg = BatchFormDialog(batch=batch, parent=self)
            if dlg.exec() == BatchFormDialog.Accepted:
                self.reload_data()

    def _open_batch_roster(self, batch_id: str):
        dlg = BatchRosterDialog(batch_id=batch_id, parent=self)
        dlg.exec()
        self.reload_data()
