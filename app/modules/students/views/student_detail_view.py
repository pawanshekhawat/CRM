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
from app.ui.widgets.form_image_viewer import FormImageViewer

class StudentDetailView(QDialog):
    """Rich Student Profile View with fee ledger, session tracker, and instant PDF printer."""

    student_updated = Signal()

    def __init__(self, student_id: str, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.student: Optional[Student] = None

        self.setWindowTitle("Student Profile & Admission Record")
        self.setMinimumSize(940, 720)
        self.resize(1020, 780)

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
        status_color = "#10B981" if s.status == "Active" else "#3B82F6" if s.status == "Completed" else "#71717A" if s.status == "Dropout" else "#EF4444"
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

        # Safely resolve assigned staff name
        assigned_faculty_name = "Unassigned"
        try:
            if s.assigned_staff:
                assigned_faculty_name = s.assigned_staff.name
        except Exception:
            if getattr(s, "assigned_staff_id", None):
                try:
                    from app.modules.staff.controllers import StaffController
                    st = StaffController.get_staff_by_id(s.assigned_staff_id)
                    if st:
                        assigned_faculty_name = st.name
                except Exception:
                    pass

        # Safely resolve enrolled batches
        enrolled_batches_str = "None"
        try:
            if s.batches:
                b_codes = [b.batch_code for b in s.batches if b]
                if b_codes:
                    enrolled_batches_str = ", ".join(b_codes)
        except Exception:
            try:
                if s.batch_enrollments:
                    b_codes = [enr.batch.batch_code for enr in s.batch_enrollments if enr.batch]
                    if b_codes:
                        enrolled_batches_str = ", ".join(b_codes)
            except Exception:
                pass

        # Safely resolve referrer details
        referred_by_str = "Direct Admission / None"
        try:
            if s.referred_by:
                referred_by_str = f"{s.referred_by.name} ({s.referred_by.id_no} • {s.referred_by.mobile_no})"
            elif getattr(s, "referred_by_student_id", None):
                ref_st = StudentController.get_student_by_id(s.referred_by_student_id)
                if ref_st:
                    referred_by_str = f"{ref_st.name} ({ref_st.id_no} • {ref_st.mobile_no})"
        except Exception:
            pass

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
            ("Enrolled Course", s.course_name or "N/A"),
            ("Assigned Faculty", assigned_faculty_name),
            ("Enrolled Batches", enrolled_batches_str),
            ("Admission Date", s.admission_date.strftime("%d/%m/%Y") if s.admission_date else "N/A"),
            ("Declaration Agreed", "Yes" if s.declaration_agreed else "No"),
            ("Referred By", referred_by_str),
            ("Referral Discount", f"₹{s.referral_discount:,.2f}" if (s.referral_discount and s.referral_discount > 0) else "None (₹0.00)"),
            ("Referrer Commission", f"₹{s.referral_commission:,.2f}" if (s.referral_commission and s.referral_commission > 0) else "None (₹0.00)"),
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

        # Tab 3: Admission Form Image Viewer
        form_tab = QWidget()
        form_layout = QVBoxLayout(form_tab)
        form_layout.setContentsMargins(12, 12, 12, 12)
        self.form_viewer = FormImageViewer(
            relative_form_path=s.admission_form_path,
            student_name=s.name,
            parent=self,
        )
        self.form_viewer.form_uploaded.connect(self._on_form_uploaded)
        form_layout.addWidget(self.form_viewer)
        tabs.addTab(form_tab, "📑 Admission Form")

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

        # Tab 5: Referrals & Commission
        referrals = []
        try:
            referrals = StudentController.get_student_referrals(s.id)
        except Exception:
            pass

        referrals_tab = QWidget()
        ref_layout = QVBoxLayout(referrals_tab)
        ref_layout.setContentsMargins(14, 14, 14, 14)
        ref_layout.setSpacing(14)

        # Top Stat KPI Cards
        stat_row = QHBoxLayout()
        stat_row.setSpacing(14)

        total_ref_count = len(referrals)
        total_comm_earned = sum((r.referral_commission or 0.0) for r in referrals)
        total_disc_given = sum((r.referral_discount or 0.0) for r in referrals)

        # 1. Total Referrals Card
        card1 = QFrame()
        card1.setStyleSheet("background-color: #101520; border: 1px solid #10B98144; border-radius: 10px; padding: 10px 14px;")
        c1_lay = QVBoxLayout(card1)
        c1_lay.setContentsMargins(0, 0, 0, 0)
        c1_lay.setSpacing(2)
        c1_val = QLabel(f"{total_ref_count}")
        c1_val.setStyleSheet("font-size: 20px; font-weight: 700; color: #10B981;")
        c1_lbl = QLabel("STUDENTS REFERRED")
        c1_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #94A3B8;")
        c1_lay.addWidget(c1_val)
        c1_lay.addWidget(c1_lbl)
        stat_row.addWidget(card1)

        # 2. Total Commission Card
        card2 = QFrame()
        card2.setStyleSheet("background-color: #101520; border: 1px solid #3B82F644; border-radius: 10px; padding: 10px 14px;")
        c2_lay = QVBoxLayout(card2)
        c2_lay.setContentsMargins(0, 0, 0, 0)
        c2_lay.setSpacing(2)
        c2_val = QLabel(f"₹{total_comm_earned:,.2f}")
        c2_val.setStyleSheet("font-size: 20px; font-weight: 700; color: #3B82F6;")
        c2_lbl = QLabel("TOTAL COMMISSION EARNED")
        c2_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #94A3B8;")
        c2_lay.addWidget(c2_val)
        c2_lay.addWidget(c2_lbl)
        stat_row.addWidget(card2)

        # 3. Total Referral Discounts Card
        card3 = QFrame()
        card3.setStyleSheet("background-color: #101520; border: 1px solid #F59E0B44; border-radius: 10px; padding: 10px 14px;")
        c3_lay = QVBoxLayout(card3)
        c3_lay.setContentsMargins(0, 0, 0, 0)
        c3_lay.setSpacing(2)
        c3_val = QLabel(f"₹{total_disc_given:,.2f}")
        c3_val.setStyleSheet("font-size: 20px; font-weight: 700; color: #F59E0B;")
        c3_lbl = QLabel("TOTAL DISCOUNTS GRANTED")
        c3_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #94A3B8;")
        c3_lay.addWidget(c3_val)
        c3_lay.addWidget(c3_lbl)
        stat_row.addWidget(card3)

        ref_layout.addLayout(stat_row)

        if referrals:
            ref_table = QTableWidget(len(referrals), 8)
            ref_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            ref_table.setFocusPolicy(Qt.NoFocus)
            ref_table.setHorizontalHeaderLabels([
                "ID No.", "Student Name", "Mobile No.", "Course Enrolled", "Admission Date", "Discount (₹)", "Commission (₹)", "Action"
            ])
            ref_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            ref_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            ref_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            ref_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)

            for r_idx, ref_s in enumerate(referrals):
                itm_id = QTableWidgetItem(ref_s.id_no)
                itm_id.setTextAlignment(Qt.AlignCenter)
                ref_table.setItem(r_idx, 0, itm_id)

                itm_name = QTableWidgetItem(ref_s.name)
                ref_table.setItem(r_idx, 1, itm_name)

                itm_mob = QTableWidgetItem(ref_s.mobile_no)
                itm_mob.setTextAlignment(Qt.AlignCenter)
                ref_table.setItem(r_idx, 2, itm_mob)

                itm_course = QTableWidgetItem(ref_s.course_name or "-")
                ref_table.setItem(r_idx, 3, itm_course)

                adm_str = ref_s.admission_date.strftime("%d/%m/%Y") if ref_s.admission_date else "-"
                itm_date = QTableWidgetItem(adm_str)
                itm_date.setTextAlignment(Qt.AlignCenter)
                ref_table.setItem(r_idx, 4, itm_date)

                disc_val = ref_s.referral_discount or 0.0
                itm_disc = QTableWidgetItem(f"₹{disc_val:,.2f}")
                itm_disc.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                ref_table.setItem(r_idx, 5, itm_disc)

                comm_val = ref_s.referral_commission or 0.0
                itm_comm = QTableWidgetItem(f"₹{comm_val:,.2f}")
                itm_comm.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                ref_table.setItem(r_idx, 6, itm_comm)

                # View Action Button
                act_w = QWidget()
                act_w.setStyleSheet("background: transparent;")
                act_l = QHBoxLayout(act_w)
                act_l.setContentsMargins(4, 2, 4, 2)
                act_l.setAlignment(Qt.AlignCenter)
                v_btn = QPushButton("👁️ View")
                v_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2563EB;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 4px;
                        padding: 3px 10px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #3B82F6;
                    }
                """)
                v_btn.clicked.connect(lambda checked=False, sid=ref_s.id: self._open_referred_student(sid))
                act_l.addWidget(v_btn)
                ref_table.setCellWidget(r_idx, 7, act_w)

            ref_table.doubleClicked.connect(lambda idx: self._open_referred_student(referrals[idx.row()].id))
            ref_layout.addWidget(ref_table)
        else:
            empty_card = QFrame()
            empty_card.setStyleSheet("background-color: #101520; border: 1.5px dashed #283347; border-radius: 12px; padding: 30px;")
            empty_layout = QVBoxLayout(empty_card)
            empty_layout.setAlignment(Qt.AlignCenter)
            empty_layout.setSpacing(8)

            icon_lbl = QLabel("🤝")
            icon_lbl.setStyleSheet("font-size: 36px;")
            icon_lbl.setAlignment(Qt.AlignCenter)
            empty_layout.addWidget(icon_lbl)

            msg_title = QLabel("No Referrals Recorded Yet")
            msg_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F1F5F9;")
            msg_title.setAlignment(Qt.AlignCenter)
            empty_layout.addWidget(msg_title)

            msg_desc = QLabel(
                f"When other students enroll and select {s.name} as 'Referred By',\n"
                "their details, the ₹4,000 referral discount, and earned commissions will automatically appear here."
            )
            msg_desc.setStyleSheet("color: #94A3B8; font-size: 12px; line-height: 1.4;")
            msg_desc.setAlignment(Qt.AlignCenter)
            empty_layout.addWidget(msg_desc)

            ref_layout.addWidget(empty_card)

        ref_layout.addStretch()
        tabs.addTab(referrals_tab, f"🤝 Referrals & Commission ({total_ref_count})")
        tabs.currentChanged.connect(lambda idx: self._on_tab_changed(idx))
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

    def _on_tab_changed(self, tab_index: int):
        # When switching to Admission Form tab (index 2)
        if tab_index == 2 and hasattr(self, "form_viewer") and self.form_viewer:
            from PySide6.QtCore import QTimer
            self.form_viewer._fit_to_view()
            QTimer.singleShot(50, self.form_viewer._fit_to_view)
            QTimer.singleShot(150, self.form_viewer._fit_to_view)

    def _open_referred_student(self, student_id: str):
        dlg = StudentDetailView(student_id=student_id, parent=self)
        dlg.student_updated.connect(self._on_child_student_updated)
        dlg.exec()

    def _on_child_student_updated(self):
        self._load_student_data()
        self._build_ui()
        self.student_updated.emit()

    def _on_form_uploaded(self, rel_path: str):
        if self.student:
            StudentController.update_student(self.student.id, {"admission_form_path": rel_path})
            self.student.admission_form_path = rel_path
            self.student_updated.emit()

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
