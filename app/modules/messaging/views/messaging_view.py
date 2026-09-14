from typing import Dict, List, Optional
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.message_template import MessageTemplate
from app.models.student import Student
from app.modules.courses.controllers import CourseController
from app.modules.messaging.controllers import MessageController
from app.modules.messaging.views.dispatch_queue_dialog import DispatchQueueDialog
from app.modules.messaging.views.template_editor_dialog import TemplateEditorDialog
from app.modules.students.controllers import StudentController
from app.ui.widgets.search_bar import SearchBar
from app.ui.widgets.stat_card import StatCard


class MessagingView(QWidget):
    """Main UI for WhatsApp message automation, template management, and bulk student dispatch."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.all_students: List[Student] = []
        self.filtered_students: List[Student] = []
        self.selected_student_ids: set = set()
        self.highlighted_student: Optional[Student] = None
        self.templates: List[MessageTemplate] = []

        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # 1. Top Header Card & Stats
        header_card = QFrame()
        header_card.setObjectName("card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)
        h_layout.setSpacing(14)

        h_info = QVBoxLayout()
        h_info.setSpacing(2)
        title_lbl = QLabel("📢 Message Automation & WhatsApp Workflows")
        title_lbl.setObjectName("headerTitle")
        title_lbl.setStyleSheet("font-size: 17px; font-weight: 800; color: #F8FAFC;")
        h_info.addWidget(title_lbl)

        sub_lbl = QLabel("Select student cohorts, compose personalized templates with Spintax, and dispatch via WhatsApp.")
        sub_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        h_info.addWidget(sub_lbl)
        h_layout.addLayout(h_info, 3)

        # Stat Badges
        self.stat_total_lbl = QLabel("Total Students: <b>0</b>")
        self.stat_total_lbl.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 6px 12px; font-size: 11.5px; color: #E2E8F0;")
        h_layout.addWidget(self.stat_total_lbl)

        self.stat_pending_lbl = QLabel("Pending Fees: <b>0</b>")
        self.stat_pending_lbl.setStyleSheet("background-color: #EF444418; border: 1px solid #EF444455; border-radius: 8px; padding: 6px 12px; font-size: 11.5px; color: #F87171;")
        h_layout.addWidget(self.stat_pending_lbl)

        self.stat_selected_lbl = QLabel("Selected: <b>0</b>")
        self.stat_selected_lbl.setStyleSheet("background-color: #10B98118; border: 1px solid #10B98155; border-radius: 8px; padding: 6px 12px; font-size: 11.5px; color: #34D399; font-weight: 700;")
        h_layout.addWidget(self.stat_selected_lbl)

        main_layout.addWidget(header_card)

        # 2. Main Two-Column Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left Column: Student Selection Table & Filters
        left_widget = self._build_left_panel()
        splitter.addWidget(left_widget)

        # Right Column: Template Selector, Composer & Live Preview
        right_widget = self._build_right_panel()
        splitter.addWidget(right_widget)

        splitter.setSizes([620, 500])
        main_layout.addWidget(splitter, 1)

    def _build_left_panel(self) -> QWidget:
        left_container = QFrame()
        left_container.setObjectName("card")
        layout = QVBoxLayout(left_container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Filter Toolbar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        self.search_bar = SearchBar(placeholder="Search Name, Mobile, Course, ID...")
        self.search_bar.searched.connect(lambda s: self._apply_filters())
        filter_bar.addWidget(self.search_bar, 3)

        self.course_filter = QComboBox()
        self.course_filter.addItem("All Courses")
        self.course_filter.setMinimumWidth(130)
        self.course_filter.currentTextChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.course_filter, 2)

        self.fee_filter = QComboBox()
        self.fee_filter.addItems(["All Fees", "Pending / Partial", "Fully Paid", "No Fee"])
        self.fee_filter.setMinimumWidth(125)
        self.fee_filter.currentTextChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.fee_filter, 2)

        layout.addLayout(filter_bar)

        # Quick Batch Selection Buttons
        quick_select_row = QHBoxLayout()
        quick_select_row.setSpacing(6)

        btn_select_all = QPushButton("☑️ Select All")
        btn_select_all.setStyleSheet("background-color: #1E293B; color: #F1F5F9; border: 1px solid #334155; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        btn_select_all.clicked.connect(self._select_all_visible)
        quick_select_row.addWidget(btn_select_all)

        btn_select_pending = QPushButton("🎯 Select Pending Fees Only")
        btn_select_pending.setStyleSheet("background-color: #7C2D12; color: #FED7AA; border: 1px solid #9A3412; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: 600;")
        btn_select_pending.clicked.connect(self._select_pending_fees_only)
        quick_select_row.addWidget(btn_select_pending)

        btn_deselect = QPushButton("⬜ Deselect All")
        btn_deselect.setStyleSheet("background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
        btn_deselect.clicked.connect(self._deselect_all)
        quick_select_row.addWidget(btn_deselect)

        quick_select_row.addStretch()
        layout.addLayout(quick_select_row)

        # Student Selection Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Select", "Student Name & ID", "Mobile", "Course", "Balance Due", "Last Fee Paid"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 48)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.Stretch)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 140)

        self.table.itemSelectionChanged.connect(self._on_table_row_selected)
        layout.addWidget(self.table, 1)

        return left_container

    def _build_right_panel(self) -> QWidget:
        right_container = QFrame()
        right_container.setObjectName("card")
        layout = QVBoxLayout(right_container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Saved Templates Row
        tmpl_header = QHBoxLayout()
        tmpl_header.setSpacing(8)

        t_lbl = QLabel("<b>📁 Saved Template:</b>")
        t_lbl.setStyleSheet("font-size: 12px; color: #F8FAFC;")
        tmpl_header.addWidget(t_lbl)

        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self._on_template_selected)
        tmpl_header.addWidget(self.template_combo, 1)

        new_tmpl_btn = QPushButton("+ New")
        new_tmpl_btn.setToolTip("Create a new reusable template")
        new_tmpl_btn.clicked.connect(self._create_new_template)
        tmpl_header.addWidget(new_tmpl_btn)

        edit_tmpl_btn = QPushButton("✏️ Edit")
        edit_tmpl_btn.setToolTip("Edit the currently selected template")
        edit_tmpl_btn.clicked.connect(self._edit_current_template)
        tmpl_header.addWidget(edit_tmpl_btn)

        del_tmpl_btn = QPushButton("🗑️")
        del_tmpl_btn.setToolTip("Delete currently selected template")
        del_tmpl_btn.clicked.connect(self._delete_current_template)
        tmpl_header.addWidget(del_tmpl_btn)

        layout.addLayout(tmpl_header)

        # Merge Tags Quick Buttons
        tags_card = QFrame()
        tags_card.setStyleSheet("background-color: #12151D; border: 1px dashed #334155; border-radius: 6px; padding: 6px;")
        tags_layout = QVBoxLayout(tags_card)
        tags_layout.setSpacing(4)
        tags_layout.setContentsMargins(4, 4, 4, 4)

        t_hint = QLabel("<b>Click Tag to Insert into Template:</b>")
        t_hint.setStyleSheet("font-size: 10.5px; color: #38BDF8;")
        tags_layout.addWidget(t_hint)

        tags_row = QHBoxLayout()
        tags_row.setSpacing(4)
        quick_tags = ["{name}", "{course}", "{balance_due}", "{last_paid_date}", "{days_ago}", "{id_no}"]
        for q_tag in quick_tags:
            btn = QPushButton(q_tag)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    color: #38BDF8;
                    border: 1px solid #0284C7;
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 10.5px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0284C7;
                    color: #FFFFFF;
                }
            """)
            btn.clicked.connect(lambda checked=False, t=q_tag: self._insert_tag_to_composer(t))
            tags_row.addWidget(btn)
        tags_row.addStretch()
        tags_layout.addLayout(tags_row)

        layout.addWidget(tags_card)

        # Message Composer Box
        layout.addWidget(QLabel("<b>Message Content / Workflow Script:</b>"))
        self.composer_edit = QTextEdit()
        self.composer_edit.setPlaceholderText("Write your WhatsApp message template with {name}, {course}, {balance_due} and Spintax {Dear|Hello}...")
        self.composer_edit.setMinimumHeight(110)
        self.composer_edit.setStyleSheet("background-color: #0F172A; border: 1px solid #283042; border-radius: 6px; padding: 8px; font-size: 12px; font-family: 'Consolas', 'Segoe UI', monospace;")
        self.composer_edit.textChanged.connect(self._update_live_preview)
        layout.addWidget(self.composer_edit)

        # Live Rendered Preview Card
        prev_header = QHBoxLayout()
        prev_header.addWidget(QLabel("<b>👁️ Live Preview for Highlighted Student:</b>"))
        self.char_count_lbl = QLabel("0 chars")
        self.char_count_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        prev_header.addStretch()
        prev_header.addWidget(self.char_count_lbl)
        layout.addLayout(prev_header)

        self.preview_box = QTextEdit()
        self.preview_box.setReadOnly(True)
        self.preview_box.setMinimumHeight(95)
        self.preview_box.setStyleSheet("background-color: #0B0F19; border: 1px solid #1E293B; border-radius: 6px; padding: 8px; font-size: 12px; color: #34D399;")
        layout.addWidget(self.preview_box)

        # Action Buttons Bottom
        act_box = QVBoxLayout()
        act_box.setSpacing(6)

        # Primary Bulk Dispatch Button
        self.start_dispatch_btn = QPushButton("⚡ Start WhatsApp Batch Dispatch (0 Selected)")
        self.start_dispatch_btn.setObjectName("primaryBtn")
        self.start_dispatch_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: #FFFFFF;
                border: 1px solid #047857;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #10B981;
                border-color: #059669;
            }
        """)
        self.start_dispatch_btn.clicked.connect(self._on_start_batch_dispatch)
        act_box.addWidget(self.start_dispatch_btn)

        # Single Student 1-Click Send Button
        self.single_send_btn = QPushButton("💬 Open WhatsApp for Highlighted Student (1-Click)")
        self.single_send_btn.setStyleSheet("background-color: #2563EB; color: #FFFFFF; border: 1px solid #1D4ED8; border-radius: 6px; padding: 7px 12px; font-weight: 600; font-size: 11.5px;")
        self.single_send_btn.clicked.connect(self._on_single_send_clicked)
        act_box.addWidget(self.single_send_btn)

        layout.addLayout(act_box)

        return right_container

    def refresh_data(self):
        """Reload students and templates from database."""
        # 1. Load Courses for filter
        courses = CourseController.get_all_courses()
        current_c = self.course_filter.currentText()
        self.course_filter.blockSignals(True)
        self.course_filter.clear()
        self.course_filter.addItem("All Courses")
        for c in courses:
            self.course_filter.addItem(c.name)
        if current_c:
            idx = self.course_filter.findText(current_c)
            if idx >= 0:
                self.course_filter.setCurrentIndex(idx)
        self.course_filter.blockSignals(False)

        # 2. Load Templates
        self.templates = MessageController.get_all_templates()
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        for tmpl in self.templates:
            self.template_combo.addItem(f"[{tmpl.category}] {tmpl.title}", tmpl.id)
        self.template_combo.blockSignals(False)

        # Load first template into composer
        if self.templates and not self.composer_edit.toPlainText().strip():
            self.composer_edit.setPlainText(self.templates[0].content or "")

        # 3. Load Students
        self.all_students = StudentController.get_all_students()
        self._apply_filters()
        self._update_kpi_stats()

    def _apply_filters(self):
        query = self.search_bar.text().strip().lower()
        course_sel = self.course_filter.currentText()
        fee_sel = self.fee_filter.currentText()

        filtered = []
        for s in self.all_students:
            # Search query filter
            if query:
                match = (
                    query in (s.name or "").lower()
                    or query in (s.mobile_no or "").lower()
                    or query in (s.course_name or "").lower()
                    or query in (s.id_no or "").lower()
                )
                if not match:
                    continue

            # Course filter
            if course_sel and course_sel != "All Courses":
                if (s.course_name or "").strip().lower() != course_sel.strip().lower():
                    continue

            # Fee filter
            if fee_sel == "Pending / Partial":
                if s.fee_status not in ("Pending", "Partial") or s.balance_due <= 0:
                    continue
            elif fee_sel == "Fully Paid":
                if s.fee_status != "Paid":
                    continue
            elif fee_sel == "No Fee":
                if s.fee_status != "No Fee":
                    continue

            filtered.append(s)

        self.filtered_students = filtered
        self._populate_table()

    def _populate_table(self):
        self.table.setRowCount(0)

        for row_idx, s in enumerate(self.filtered_students):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 46)

            # 0. Checkbox
            chk = QCheckBox()
            chk.setStyleSheet("margin-left: 14px;")
            chk.setChecked(s.id in self.selected_student_ids)
            chk.toggled.connect(lambda checked, sid=s.id: self._on_student_toggled(sid, checked))
            self.table.setCellWidget(row_idx, 0, chk)

            # 1. Student Name & ID
            name_widget = QWidget()
            name_widget.setStyleSheet("background: transparent;")
            n_layout = QVBoxLayout(name_widget)
            n_layout.setContentsMargins(4, 2, 4, 2)
            n_layout.setSpacing(1)
            n_layout.setAlignment(Qt.AlignVCenter)

            n_lbl = QLabel(s.name)
            n_lbl.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 12.5px;")
            id_lbl = QLabel(f"ID: {s.id_no}")
            id_lbl.setStyleSheet("color: #64748B; font-size: 10.5px;")

            n_layout.addWidget(n_lbl)
            n_layout.addWidget(id_lbl)
            self.table.setCellWidget(row_idx, 1, name_widget)

            # 2. Mobile Number
            mob_item = QTableWidgetItem(s.mobile_no)
            mob_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, mob_item)

            # 3. Course
            c_item = QTableWidgetItem(s.course_name or "-")
            self.table.setItem(row_idx, 3, c_item)

            # 4. Balance Due
            bal = s.balance_due
            bal_str = f"₹{bal:,.0f}" if bal > 0 else "₹0"
            bal_item = QTableWidgetItem(bal_str)
            bal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if bal > 0:
                bal_item.setForeground(Qt.red)
            self.table.setItem(row_idx, 4, bal_item)

            # 5. Last Fee Paid
            last_pay_str = s.last_payment_summary
            lp_item = QTableWidgetItem(last_pay_str)
            lp_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, lp_item)

        if self.filtered_students:
            if not self.highlighted_student:
                self.highlighted_student = self.filtered_students[0]
            self.table.selectRow(0)
            self._update_live_preview()

    def _on_student_toggled(self, student_id: str, is_checked: bool):
        if is_checked:
            self.selected_student_ids.add(student_id)
        else:
            self.selected_student_ids.discard(student_id)
        self._update_selected_count_ui()

    def _select_all_visible(self):
        for s in self.filtered_students:
            self.selected_student_ids.add(s.id)
        self._populate_table()
        self._update_selected_count_ui()

    def _select_pending_fees_only(self):
        self.selected_student_ids.clear()
        for s in self.filtered_students:
            if s.balance_due > 0:
                self.selected_student_ids.add(s.id)
        self._populate_table()
        self._update_selected_count_ui()

    def _deselect_all(self):
        self.selected_student_ids.clear()
        self._populate_table()
        self._update_selected_count_ui()

    def _on_table_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            r = rows[0].row()
            if r < len(self.filtered_students):
                self.highlighted_student = self.filtered_students[r]
                self._update_live_preview()

    def _update_selected_count_ui(self):
        count = len(self.selected_student_ids)
        self.stat_selected_lbl.setText(f"Selected: <b>{count}</b>")
        self.start_dispatch_btn.setText(f"⚡ Start WhatsApp Batch Dispatch ({count} Selected)")
        self.start_dispatch_btn.setEnabled(count > 0)

    def _update_kpi_stats(self):
        total = len(self.all_students)
        pending = sum(1 for s in self.all_students if s.balance_due > 0)
        self.stat_total_lbl.setText(f"Total Students: <b>{total}</b>")
        self.stat_pending_lbl.setText(f"Pending Fees: <b>{pending}</b>")
        self._update_selected_count_ui()

    def _on_template_selected(self, index: int):
        if index < 0 or index >= len(self.templates):
            return
        tmpl = self.templates[index]
        self.composer_edit.setPlainText(tmpl.content or "")

    def _insert_tag_to_composer(self, tag_text: str):
        self.composer_edit.insertPlainText(tag_text)
        self.composer_edit.setFocus()

    def _update_live_preview(self):
        template_text = self.composer_edit.toPlainText().strip()
        self.char_count_lbl.setText(f"{len(template_text)} chars")

        if not self.highlighted_student:
            self.preview_box.setPlainText("Select a student on the left to see live personalized preview.")
            return

        rendered = MessageController.render_message(template_text, self.highlighted_student, randomize_spintax=False)
        self.preview_box.setPlainText(rendered)
        self.single_send_btn.setText(f"💬 Open WhatsApp for {self.highlighted_student.name} (1-Click)")

    def _create_new_template(self):
        dlg = TemplateEditorDialog(parent=self)
        if dlg.exec():
            self.refresh_data()

    def _edit_current_template(self):
        idx = self.template_combo.currentIndex()
        if idx < 0 or idx >= len(self.templates):
            return
        tmpl = self.templates[idx]
        dlg = TemplateEditorDialog(template=tmpl, parent=self)
        if dlg.exec():
            self.refresh_data()

    def _delete_current_template(self):
        idx = self.template_combo.currentIndex()
        if idx < 0 or idx >= len(self.templates):
            return
        tmpl = self.templates[idx]
        reply = QMessageBox.question(
            self,
            "Delete Template",
            f"Are you sure you want to delete template '{tmpl.title}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            MessageController.delete_template(tmpl.id)
            self.refresh_data()

    def _on_single_send_clicked(self):
        if not self.highlighted_student:
            QMessageBox.warning(self, "No Student Selected", "Please select a student from the table.")
            return

        msg = self.preview_box.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Empty Message", "Message content cannot be empty.")
            return

        url = MessageController.build_whatsapp_url(self.highlighted_student.mobile_no, msg, use_desktop_app=True)
        QDesktopServices.openUrl(QUrl(url))

    def _on_start_batch_dispatch(self):
        selected_students = [s for s in self.all_students if s.id in self.selected_student_ids]
        if not selected_students:
            QMessageBox.warning(self, "No Students Selected", "Please select at least one student from the table.")
            return

        template_text = self.composer_edit.toPlainText().strip()
        if not template_text:
            QMessageBox.warning(self, "Empty Message", "Please compose a message template before dispatching.")
            return

        # Launch Dispatch Queue Dialog
        queue_dlg = DispatchQueueDialog(students=selected_students, template_text=template_text, parent=self)
        queue_dlg.exec()
