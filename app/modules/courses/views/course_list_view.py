from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.course import Course
from app.modules.courses.controllers import CourseController
from app.modules.courses.views.course_form_dialog import CourseFormDialog
from app.ui.widgets.stat_card import StatCard

class CourseListView(QWidget):
    """Main Management View for Course Programs, Standard Fees & Durations."""

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

        title = QLabel("Courses & Fee Catalog")
        title.setObjectName("pageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC;")
        header_text.addWidget(title)

        subtitle = QLabel("Standardized course programs, fixed fee structures, syllabus outlines, and enrollment statistics.")
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        header_text.addWidget(subtitle)

        top_bar.addLayout(header_text)
        top_bar.addStretch()

        # Add Course Button
        self.add_course_btn = QPushButton("➕ Add New Course")
        self.add_course_btn.setObjectName("primaryBtn")
        self.add_course_btn.clicked.connect(self._on_add_course)
        top_bar.addWidget(self.add_course_btn)

        main_layout.addLayout(top_bar)

        # 2. Stat Summary Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        self.card_total_courses = StatCard("Total Programs", "0", "Catalog courses", "🎓", "#3B82F6")
        self.card_active_courses = StatCard("Active Courses", "0", "Open for admission", "✅", "#10B981")
        self.card_avg_fee = StatCard("Avg Course Fee", "₹0", "Mean standard price", "💰", "#F59E0B")
        self.card_categories = StatCard("Categories", "0", "Specialized streams", "📑", "#8B5CF6")

        stats_layout.addWidget(self.card_total_courses)
        stats_layout.addWidget(self.card_active_courses)
        stats_layout.addWidget(self.card_avg_fee)
        stats_layout.addWidget(self.card_categories)

        main_layout.addLayout(stats_layout)

        # 3. Filters Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search course name, code, category, syllabus keywords...")
        self.search_input.textChanged.connect(self.reload_course_table)
        filter_bar.addWidget(self.search_input, stretch=2)

        filter_bar.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All",
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
        ])
        self.category_filter.currentTextChanged.connect(self.reload_course_table)
        filter_bar.addWidget(self.category_filter)

        filter_bar.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Inactive", "Archived"])
        self.status_filter.currentTextChanged.connect(self.reload_course_table)
        filter_bar.addWidget(self.status_filter)

        main_layout.addLayout(filter_bar)

        # 4. Courses Table (7 columns)
        self.table = QTableWidget(0, 7)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setHorizontalHeaderLabels([
            "Code", "Course Name", "Category / Stream", "Standard Fee (₹)", "Enrolled", "Status", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        main_layout.addWidget(self.table)

    def reload_data(self):
        """Refreshes metrics and table."""
        metrics = CourseController.get_courses_dashboard_metrics()
        self.card_total_courses.set_value(str(metrics["total_courses"]))
        self.card_active_courses.set_value(str(metrics["active_courses"]))
        self.card_avg_fee.set_value(f"₹{metrics['avg_fee']:,.0f}")
        self.card_categories.set_value(str(metrics["categories_count"]))

        self.reload_course_table()

    def reload_course_table(self):
        search = self.search_input.text().strip() or None
        cat = self.category_filter.currentText()
        st = self.status_filter.currentText()

        courses = CourseController.get_all_courses(search=search, category=cat, status=st)
        self.table.setRowCount(0)

        for row_idx, c in enumerate(courses):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 46)

            # 0. Code
            code_item = QTableWidgetItem(c.course_code)
            code_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, code_item)

            # 1. Course Name
            name_item = QTableWidgetItem(f" {c.name} ")
            f = QFont()
            f.setBold(True)
            name_item.setFont(f)
            self.table.setItem(row_idx, 1, name_item)

            # 2. Category
            self.table.setItem(row_idx, 2, QTableWidgetItem(c.category or "-"))

            # 3. Standard Fee
            fee_item = QTableWidgetItem(f"₹{c.standard_fee:,.2f}")
            fee_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            f_font = QFont()
            f_font.setBold(True)
            fee_item.setFont(f_font)
            fee_item.setForeground(Qt.green)
            self.table.setItem(row_idx, 3, fee_item)

            # 4. Enrolled Students
            stats = CourseController.get_course_stats(c.name)
            enr_item = QTableWidgetItem(f"👥 {stats['student_count']} std | 📚 {stats['batch_count']} bat")
            enr_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, enr_item)

            # 5. Status Badge
            st_color = "#10B981" if c.status == "Active" else "#64748B"
            st_badge = QLabel(f" {c.status} ")
            st_badge.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {st_color}; background-color: {st_color}22; border: 1px solid {st_color}55; border-radius: 6px; padding: 2px 6px;")
            st_badge.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row_idx, 5, st_badge)

            # 6. Actions
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setSpacing(6)
            a_layout.setAlignment(Qt.AlignCenter)

            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            edit_btn.clicked.connect(lambda _, c_id=c.id: self._on_edit_course(c_id))
            a_layout.addWidget(edit_btn)

            del_btn = QPushButton("🗑️")
            del_btn.setStyleSheet("padding: 4px 6px; font-size: 11px; background: #EF444422; color: #EF4444; border: 1px solid #EF444455;")
            del_btn.clicked.connect(lambda _, c_id=c.id, c_name=c.name: self._on_delete_course(c_id, c_name))
            a_layout.addWidget(del_btn)

            self.table.setCellWidget(row_idx, 6, action_widget)

    def _on_add_course(self):
        dlg = CourseFormDialog(parent=self)
        if dlg.exec() == CourseFormDialog.Accepted:
            self.reload_data()

    def _on_edit_course(self, course_id: str):
        course = CourseController.get_course_by_id(course_id)
        if course:
            dlg = CourseFormDialog(course=course, parent=self)
            if dlg.exec() == CourseFormDialog.Accepted:
                self.reload_data()

    def _on_delete_course(self, course_id: str, course_name: str):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete course '{course_name}' from the catalog?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            CourseController.delete_course(course_id)
            self.reload_data()
