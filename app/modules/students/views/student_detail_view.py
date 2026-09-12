import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
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
from app.models.student import Student
from app.modules.students.controllers import StudentController
from app.modules.students.reports import ReportGenerator
from app.modules.students.views.student_form_dialog import StudentFormDialog

class StudentDetailView(QDialog):
    """Rich Student Profile View with fee ledger, session tracker, and instant PDF printer."""

    student_updated = Signal()

    def __init__(self, student_id: str, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.student: Optional[Student] = None

        self.setWindowTitle("Student Profile & Admission Record")
        self.setMinimumSize(880, 640)
        self.resize(960, 700)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(18, 18, 18, 18)
        self.main_layout.setSpacing(14)

        self._load_student_data()
        self._build_ui()

    def _load_student_data(self):
        self.student = StudentController.get_student_by_id(self.student_id)

    def _build_ui(self):
        # Clear existing layout widgets if re-building
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.student:
            self.main_layout.addWidget(QLabel("Student record not found."))
            return

        s = self.student

        # 1. Top Header Profile Card
        header_card = QFrame()
        header_card.setObjectName("card")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 14, 16, 14)
        h_layout.setSpacing(18)

        # Photo
        photo_label = QLabel()
        photo_label.setFixedSize(85, 105)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("background-color: #151821; border: 1px solid #333C4E; border-radius: 6px;")
        if s.photo_path:
            p_file = PHOTOS_DIR / s.photo_path
            if p_file.exists():
                pix = QPixmap(str(p_file)).scaled(85, 105, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                photo_label.setPixmap(pix)
            else:
                photo_label.setText("No Photo")
        else:
            photo_label.setText("No Photo")
        h_layout.addWidget(photo_label)

        # Main Info
        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name_lbl = QLabel(s.name)
        name_lbl.setObjectName("headerTitle")
        info_col.addWidget(name_lbl)

        sub_info = QLabel(f"<b>ID No:</b> {s.id_no} &nbsp;|&nbsp; <b>Course:</b> {s.course_name or 'N/A'} &nbsp;|&nbsp; <b>Mobile:</b> {s.mobile_no}")
        sub_info.setStyleSheet("color: #94A3B8; font-size: 13px;")
        info_col.addWidget(sub_info)

        badges_row = QHBoxLayout()
        badges_row.setSpacing(8)

        # Status Badge
        status_color = "#10B981" if s.status == "Active" else "#3B82F6" if s.status == "Completed" else "#EF4444"
        status_badge = QLabel(f" {s.status} ")
        status_badge.setStyleSheet(f"background-color: {status_color}22; color: {status_color}; border: 1px solid {status_color}55; border-radius: 10px; font-size: 11px; font-weight: 600; padding: 2px 8px;")
        badges_row.addWidget(status_badge)

        # Fee Status Badge
        fee_col = "#10B981" if s.fee_status == "Paid" else "#F59E0B" if s.fee_status == "Partial" else "#EF4444"
        fee_badge = QLabel(f" Fee: {s.fee_status} (Bal: ₹{s.balance_due:,.2f}) ")
        fee_badge.setStyleSheet(f"background-color: {fee_col}22; color: {fee_col}; border: 1px solid {fee_col}55; border-radius: 10px; font-size: 11px; font-weight: 600; padding: 2px 8px;")
        badges_row.addWidget(fee_badge)

        if s.is_online:
            online_badge = QLabel(" Online Reg ")
            online_badge.setStyleSheet("background-color: #8B5CF622; color: #A78BFA; border: 1px solid #8B5CF655; border-radius: 10px; font-size: 11px; font-weight: 600; padding: 2px 8px;")
            badges_row.addWidget(online_badge)

        badges_row.addStretch()
        info_col.addLayout(badges_row)
        h_layout.addLayout(info_col, 4)

        # Right Action Buttons
        act_col = QVBoxLayout()
        act_col.setSpacing(6)

        print_btn = QPushButton("📄 Print Admission Slip (PDF)")
        print_btn.setObjectName("primaryBtn")
        print_btn.clicked.connect(self._on_print_pdf)
        act_col.addWidget(print_btn)

        edit_btn = QPushButton("✏️ Edit Details")
        edit_btn.clicked.connect(self._on_edit)
        act_col.addWidget(edit_btn)

        h_layout.addLayout(act_col, 2)
        self.main_layout.addWidget(header_card)

        # 2. Main Tab Content
        tabs = QTabWidget()

        # Tab 1: Personal & Contact Overview
        overview_tab = QWidget()
        ov_layout = QVBoxLayout(overview_tab)
        ov_grid = QGridLayout()
        ov_grid.setHorizontalSpacing(16)
        ov_grid.setVerticalSpacing(10)

        details = [
            ("Student Name", s.name),
            ("Father's Name", s.father_name or "N/A"),
            ("Mother's Name", s.mother_name or "N/A"),
            ("Father's Occupation", s.father_occupation or "N/A"),
            ("Date of Birth", s.dob.strftime("%d/%m/%Y") if s.dob else "N/A"),
            ("Aadhar Number", s.aadhar_no or "N/A"),
            ("College / School", s.college_school or "N/A"),
            ("Year / Semester", s.year_sem or "N/A"),
            ("Primary Mobile", s.mobile_no),
            ("Email Address", s.email or "N/A"),
            ("Father's Contact", s.father_contact_no or "N/A"),
            ("Alternate Contact (2.)", s.alternate_contact_no or "N/A"),
            ("Permanent Address", s.permanent_address or "N/A"),
            ("District / State / PIN", f"{s.district or ''}, {s.state or ''} - {s.pin_code or ''}"),
            ("Admission Date", s.admission_date.strftime("%d/%m/%Y") if s.admission_date else "N/A"),
            ("Declaration Agreed", "Yes" if s.declaration_agreed else "No"),
        ]

        row = 0
        col = 0
        for lbl_text, val_text in details:
            lbl = QLabel(lbl_text + ":")
            lbl.setStyleSheet("font-weight: 600; color: #94A3B8; font-size: 12px;")
            val = QLabel(str(val_text))
            val.setStyleSheet("color: #F1F5F9; font-size: 13px;")

            ov_grid.addWidget(lbl, row, col * 2)
            ov_grid.addWidget(val, row, col * 2 + 1)

            col += 1
            if col >= 2:
                col = 0
                row += 1

        ov_layout.addLayout(ov_grid)
        ov_layout.addStretch()
        tabs.addTab(overview_tab, "📋 Personal & Academic")

        # Tab 2: Fee Ledger & Installments
        fee_tab = QWidget()
        fee_layout = QVBoxLayout(fee_tab)

        # Fee Summary Cards
        f_sum_row = QHBoxLayout()
        f_sum_row.addWidget(QLabel(f"<b>Total Course Fee:</b> ₹{s.total_fee:,.2f}"))
        f_sum_row.addWidget(QLabel(f"<b>Discount:</b> ₹{s.discount_amount:,.2f}"))
        f_sum_row.addWidget(QLabel(f"<b>Net Fee:</b> ₹{s.net_fee:,.2f}"))
        f_sum_row.addWidget(QLabel(f"<b>Total Paid:</b> ₹{s.total_paid:,.2f}"))
        f_sum_row.addWidget(QLabel(f"<b>Balance Due:</b> ₹{s.balance_due:,.2f}"))
        f_sum_row.addStretch()
        fee_layout.addLayout(f_sum_row)

        inst_table = QTableWidget(0, 7)
        inst_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        inst_table.setFocusPolicy(Qt.NoFocus)
        inst_table.setHorizontalHeaderLabels([
            "Installment", "Due (₹)", "Paid (₹)", "Pay Date", "Mode", "Receipt / Ref", "Status"
        ])
        inst_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        installments = s.fee_installments or []
        running_due = float(s.net_fee or 0.0)
        for idx, inst in enumerate(installments):
            inst_table.insertRow(idx)
            paid_amt = float(inst.paid_amount or 0.0)

            # Running due balance logic
            if paid_amt > 0 or idx == 0:
                cur_due = running_due
            elif running_due > 0 and idx > 0 and (float(installments[idx - 1].paid_amount or 0.0) > 0):
                cur_due = running_due
            elif inst.due_amount and inst.due_amount > 0:
                cur_due = float(inst.due_amount)
            else:
                cur_due = 0.0

            # Status determination
            if paid_amt > 0:
                status_text = "Paid"
            elif cur_due > 0:
                status_text = "Pending"
            else:
                status_text = "Pending"

            item_label = QTableWidgetItem(inst.installment_label)
            item_due = QTableWidgetItem(f"₹{cur_due:,.2f}")
            item_paid = QTableWidgetItem(f"₹{paid_amt:,.2f}")
            item_date = QTableWidgetItem(inst.payment_date.strftime("%d/%m/%Y") if inst.payment_date else "-")
            item_mode = QTableWidgetItem(inst.payment_mode or "-")
            item_ref = QTableWidgetItem(inst.transaction_ref or "-")
            item_status = QTableWidgetItem(status_text)

            for col_idx, itm in enumerate([item_label, item_due, item_paid, item_date, item_mode, item_ref, item_status]):
                itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                if col_idx in (1, 2):
                    itm.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    itm.setTextAlignment(Qt.AlignCenter)
                inst_table.setItem(idx, col_idx, itm)

            running_due = max(0.0, running_due - paid_amt)

        fee_layout.addWidget(inst_table)
        tabs.addTab(fee_tab, "💰 Fee Ledger & Installments")

        # Tab 4: Dynamic Custom Fields
        custom_tab = QWidget()
        c_layout = QVBoxLayout(custom_tab)
        c_grid = QGridLayout()
        c_grid.setHorizontalSpacing(16)
        c_grid.setVerticalSpacing(10)

        defs = StudentController.get_custom_field_definitions("student")
        vals = StudentController.get_student_custom_values(s.id)

        if defs:
            for idx, df in enumerate(defs):
                val_str = vals.get(df.id, "N/A")
                lbl = QLabel(df.field_label + ":")
                lbl.setStyleSheet("font-weight: 600; color: #94A3B8;")
                val = QLabel(str(val_str) if val_str else "N/A")
                val.setStyleSheet("color: #F1F5F9;")
                c_grid.addWidget(lbl, idx, 0)
                c_grid.addWidget(val, idx, 1)
            c_layout.addLayout(c_grid)
        else:
            c_layout.addWidget(QLabel("No custom fields configured for this institute."))

        c_layout.addStretch()
        tabs.addTab(custom_tab, "🧩 Custom Fields")

        self.main_layout.addWidget(tabs)

        # Bottom Close / Delete Row
        b_row = QHBoxLayout()
        del_btn = QPushButton("🗑️ Delete Record")
        del_btn.setObjectName("dangerBtn")
        del_btn.clicked.connect(self._on_delete)
        b_row.addWidget(del_btn)

        b_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(90)
        close_btn.clicked.connect(self.accept)
        b_row.addWidget(close_btn)

        self.main_layout.addLayout(b_row)

    def _on_print_pdf(self):
        try:
            pdf_path = ReportGenerator.generate_admission_slip_pdf(self.student)
            QMessageBox.information(self, "PDF Generated", f"Admission Slip & Receipt PDF created successfully:\n{pdf_path}")
            # Open PDF in default viewer
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {e}")

    def _on_edit(self):
        dlg = StudentFormDialog(student=self.student, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self._load_student_data()
            self._build_ui()
            self.student_updated.emit()

    def _on_delete(self):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete {self.student.name} ({self.student.id_no})?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            StudentController.delete_student(self.student.id)
            self.student_updated.emit()
            self.accept()
