from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.config import PHOTOS_DIR
from app.models.student import Student
from app.modules.students.controllers import StudentController
from app.ui.widgets.dynamic_fields import DynamicFieldsWidget

class StudentFormDialog(QDialog):
    """Refined Admission & Student Form matching CADDESK Centre physical form."""

    def __init__(self, student: Optional[Student] = None, parent=None):
        super().__init__(parent)
        self.student = student
        self.is_edit = student is not None
        self.selected_photo_path: Optional[str] = student.photo_path if student else None
        self.temp_photo_file: Optional[str] = None

        self.setWindowTitle("Edit Student Admission" if self.is_edit else "New Student Admission (CADDESK Form)")
        self.setMinimumSize(960, 720)
        self.resize(1060, 820)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scrollable container for the extensive form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(18)

        # Build Form Sections
        self._build_header_section()
        self._build_personal_section()
        self._build_contact_section()
        self._build_fees_installment_section()
        self._build_custom_fields_section()
        self._build_declaration_section()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Bottom Action Bar (Fixed / Sticky footer)
        bottom_bar = QFrame()
        bottom_bar.setStyleSheet("background-color: #0D1017; border-top: 1px solid #1F293D;")
        bottom_bar_layout = QHBoxLayout(bottom_bar)
        bottom_bar_layout.setContentsMargins(20, 14, 20, 14)
        bottom_bar_layout.setSpacing(14)
        
        status_lbl = QLabel("Student Status:")
        status_lbl.setStyleSheet("font-weight: 600; color: #94A3B8;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Completed", "Dropped", "Inquiry"])
        self.status_combo.setMinimumWidth(140)
        bottom_bar_layout.addWidget(status_lbl)
        bottom_bar_layout.addWidget(self.status_combo)
        
        bottom_bar_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        bottom_bar_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Save Admission Record" if not self.is_edit else "💾 Update Record")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumWidth(190)
        save_btn.clicked.connect(self._on_save)
        bottom_bar_layout.addWidget(save_btn)

        main_layout.addWidget(bottom_bar)

        # Populate if edit mode
        if self.is_edit:
            self._populate_data()
        else:
            self.id_input.setText(StudentController.generate_next_id_no())

    def _build_header_section(self):
        """Header Identity Box: ID No, Online Reg, and Student Photo frame."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(24)

        # Left Column: Identity Form
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)

        org_label = QLabel("CADDESK CENTRE • ADMISSION FORM")
        org_label.setObjectName("headerTitle")
        left_layout.addWidget(org_label)

        sub_label = QLabel("SKILL INDIA & MSME AFFILIATED CENTRE")
        sub_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #EF4444; letter-spacing: 0.5px;")
        left_layout.addWidget(sub_label)
        left_layout.addSpacing(4)

        id_row = QHBoxLayout()
        id_row.setSpacing(12)
        
        id_lbl = QLabel("ID No. *")
        id_lbl.setStyleSheet("font-weight: 600; color: #F1F5F9;")
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. CD-2026-0001")
        self.id_input.setMinimumWidth(180)
        id_row.addWidget(id_lbl)
        id_row.addWidget(self.id_input)

        auto_btn = QPushButton("⚡ Auto ID")
        auto_btn.setToolTip("Generate next sequential ID")
        auto_btn.clicked.connect(lambda: self.id_input.setText(StudentController.generate_next_id_no()))
        id_row.addWidget(auto_btn)

        id_row.addSpacing(10)
        self.online_check = QCheckBox("Online Admission")
        self.online_check.stateChanged.connect(self._on_online_toggle)
        id_row.addWidget(self.online_check)

        self.online_reg_input = QLineEdit()
        self.online_reg_input.setPlaceholderText("Online Portal Reg No.")
        self.online_reg_input.setEnabled(False)
        id_row.addWidget(self.online_reg_input)

        left_layout.addLayout(id_row)

        date_row = QHBoxLayout()
        date_lbl = QLabel("Admission Date:")
        date_lbl.setStyleSheet("font-weight: 600; color: #94A3B8;")
        self.adm_date_edit = QDateEdit()
        self.adm_date_edit.setCalendarPopup(True)
        self.adm_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.adm_date_edit.setDate(QDate.currentDate())
        self.adm_date_edit.setMinimumWidth(140)
        date_row.addWidget(date_lbl)
        date_row.addWidget(self.adm_date_edit)
        date_row.addStretch()
        left_layout.addLayout(date_row)

        card_layout.addLayout(left_layout, 4)

        # Right Column: Photo Frame
        photo_box = QVBoxLayout()
        photo_box.setAlignment(Qt.AlignCenter)
        photo_box.setSpacing(8)

        self.photo_preview = QLabel("Paste Photo\nHere")
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setFixedSize(110, 130)
        self.photo_preview.setStyleSheet("""
            background-color: #0F131C;
            border: 1.5px dashed #334155;
            border-radius: 8px;
            color: #64748B;
            font-size: 11px;
            font-weight: 500;
        """)
        photo_box.addWidget(self.photo_preview)

        photo_btn_row = QHBoxLayout()
        choose_photo_btn = QPushButton("📷 Choose")
        choose_photo_btn.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        choose_photo_btn.clicked.connect(self._on_choose_photo)
        photo_btn_row.addWidget(choose_photo_btn)

        clear_photo_btn = QPushButton("✕")
        clear_photo_btn.setStyleSheet("padding: 4px 8px; font-size: 11px;")
        clear_photo_btn.clicked.connect(self._on_clear_photo)
        photo_btn_row.addWidget(clear_photo_btn)

        photo_box.addLayout(photo_btn_row)
        card_layout.addLayout(photo_box, 1)

        self.content_layout.addWidget(card)

    def _on_online_toggle(self, state):
        self.online_reg_input.setEnabled(self.online_check.isChecked())

    def _on_choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Student Photo", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            self.temp_photo_file = file_path
            self._display_photo(file_path)

    def _on_clear_photo(self):
        self.temp_photo_file = None
        self.selected_photo_path = None
        self.photo_preview.setText("Paste Photo\nHere")
        self.photo_preview.setPixmap(QPixmap())

    def _display_photo(self, path_or_name: str):
        p = Path(path_or_name)
        if not p.is_absolute():
            p = PHOTOS_DIR / path_or_name
        if p.exists():
            pix = QPixmap(str(p)).scaled(110, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_preview.setPixmap(pix)

    def _build_personal_section(self):
        """Personal details: Name, Father, Mother, DOB, Father's Occ, College, Course, Year/Sem, Aadhar."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("👤 Personal & Academic Information")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)

        # Row 0: Name & Father's Name
        grid.addWidget(QLabel("NAME *"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Student Full Name")
        grid.addWidget(self.name_input, 0, 1)

        grid.addWidget(QLabel("Father's Name"), 0, 2)
        self.father_name_input = QLineEdit()
        grid.addWidget(self.father_name_input, 0, 3)

        # Row 1: Mother's Name & Father's Occupation
        grid.addWidget(QLabel("Mother's Name"), 1, 0)
        self.mother_name_input = QLineEdit()
        grid.addWidget(self.mother_name_input, 1, 1)

        grid.addWidget(QLabel("Father's Occupation"), 1, 2)
        self.father_occ_input = QLineEdit()
        grid.addWidget(self.father_occ_input, 1, 3)

        # Row 2: Date of Birth & Aadhar No.
        grid.addWidget(QLabel("D.O.B. (dd/mm/yyyy)"), 2, 0)
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDisplayFormat("dd/MM/yyyy")
        self.dob_input.setDate(QDate(2002, 1, 1))
        grid.addWidget(self.dob_input, 2, 1)

        grid.addWidget(QLabel("Aadhar No."), 2, 2)
        self.aadhar_input = QLineEdit()
        self.aadhar_input.setPlaceholderText("12-digit UIDAI No.")
        grid.addWidget(self.aadhar_input, 2, 3)

        # Row 3: College/School & Year/Sem
        grid.addWidget(QLabel("College/School"), 3, 0)
        self.college_input = QLineEdit()
        grid.addWidget(self.college_input, 3, 1)

        grid.addWidget(QLabel("Year / Sem."), 3, 2)
        self.year_sem_input = QLineEdit()
        self.year_sem_input.setPlaceholderText("e.g. 2nd Year / 4th Sem")
        grid.addWidget(self.year_sem_input, 3, 3)

        # Row 4: Primary Course Name
        grid.addWidget(QLabel("Course Name *"), 4, 0)
        self.course_name_input = QLineEdit()
        self.course_name_input.setPlaceholderText("e.g. Full Stack Development / AutoCAD")
        grid.addWidget(self.course_name_input, 4, 1, 1, 3)

        card_layout.addLayout(grid)
        self.content_layout.addWidget(card)

    def _build_contact_section(self):
        """Contact & Address Details."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("📞 Contact & Address Details")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)

        # Row 0: Mobile & Email
        grid.addWidget(QLabel("Mob. No. *"), 0, 0)
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("10-digit mobile number")
        grid.addWidget(self.mobile_input, 0, 1)

        grid.addWidget(QLabel("E-mail id"), 0, 2)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("student@example.com")
        grid.addWidget(self.email_input, 0, 3)

        # Row 1: Father's Contact & Alternate Contact (2.)
        grid.addWidget(QLabel("Father's Contact No."), 1, 0)
        self.father_contact_input = QLineEdit()
        grid.addWidget(self.father_contact_input, 1, 1)

        grid.addWidget(QLabel("2. Alternate Contact"), 1, 2)
        self.alt_contact_input = QLineEdit()
        grid.addWidget(self.alt_contact_input, 1, 3)

        # Row 2: Permanent Address
        grid.addWidget(QLabel("Permanent Address"), 2, 0)
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("House No., Street, Area/Village")
        self.address_input.setMaximumHeight(65)
        grid.addWidget(self.address_input, 2, 1, 1, 3)

        # Row 3: District, State, PIN
        grid.addWidget(QLabel("District"), 3, 0)
        self.district_input = QLineEdit()
        grid.addWidget(self.district_input, 3, 1)

        state_pin_row = QHBoxLayout()
        state_pin_row.setSpacing(10)
        state_pin_row.addWidget(QLabel("State:"))
        self.state_input = QLineEdit()
        self.state_input.setText("Rajasthan")
        state_pin_row.addWidget(self.state_input)

        state_pin_row.addWidget(QLabel("PIN:"))
        self.pin_input = QLineEdit()
        state_pin_row.addWidget(self.pin_input)

        grid.addLayout(state_pin_row, 3, 2, 1, 2)

        card_layout.addLayout(grid)
        self.content_layout.addWidget(card)

    def _build_fees_installment_section(self):
        """Fee Structure & 10 Installments Table."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        title = QLabel("💰 Fees & 10-Installment Payment Schedule")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        # Top Total / Discount / Net Fee Controls
        fee_controls = QHBoxLayout()
        fee_controls.setSpacing(16)

        fee_controls.addWidget(QLabel("Total Fee (₹):"))
        self.total_fee_spin = QDoubleSpinBox()
        self.total_fee_spin.setRange(0, 10000000)
        self.total_fee_spin.setDecimals(2)
        self.total_fee_spin.setSingleStep(500)
        self.total_fee_spin.valueChanged.connect(self._recalc_net_fee)
        fee_controls.addWidget(self.total_fee_spin)

        fee_controls.addWidget(QLabel("Discount / Schol. (₹):"))
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 10000000)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setSingleStep(500)
        self.discount_spin.valueChanged.connect(self._recalc_net_fee)
        fee_controls.addWidget(self.discount_spin)

        fee_controls.addWidget(QLabel("Net Payable (₹):"))
        self.net_fee_spin = QDoubleSpinBox()
        self.net_fee_spin.setRange(0, 10000000)
        self.net_fee_spin.setDecimals(2)
        self.net_fee_spin.setReadOnly(True)
        self.net_fee_spin.setStyleSheet("background-color: #101520; font-weight: bold; color: #10B981; border: 1.5px solid #10B98166;")
        fee_controls.addWidget(self.net_fee_spin)

        card_layout.addLayout(fee_controls)

        # 10 Installment Grid Table
        self.inst_table = QTableWidget(10, 7)
        self.inst_table.setHorizontalHeaderLabels([
            "Installment", "Due Amt (₹)", "Paid Amt (₹)", "Payment Date", "Payment Mode", "Receipt / UTR No.", "Remarks"
        ])
        self.inst_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.inst_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.inst_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.inst_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.inst_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.inst_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.inst_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.inst_table.verticalHeader().setVisible(False)
        self.inst_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.inst_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        ordinal_labels = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
        for row_idx, label in enumerate(ordinal_labels):
            self.inst_table.setRowHeight(row_idx, 40)
            lbl_item = QTableWidgetItem(f" {label} ")
            lbl_item.setTextAlignment(Qt.AlignCenter)
            lbl_item.setFlags(lbl_item.flags() ^ Qt.ItemIsEditable)
            self.inst_table.setItem(row_idx, 0, lbl_item)

            # Due Amount (Auto-computed running ledger balance)
            due_spin = QDoubleSpinBox()
            due_spin.setRange(0, 10000000)
            due_spin.setDecimals(2)
            due_spin.setReadOnly(True)
            due_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
            due_spin.setStyleSheet("background-color: #121824; color: #94A3B8; border: 1px solid #1E293B; border-radius: 6px; padding: 2px 6px;")
            self.inst_table.setCellWidget(row_idx, 1, due_spin)

            # Paid Amount
            paid_spin = QDoubleSpinBox()
            paid_spin.setRange(0, 10000000)
            paid_spin.setDecimals(2)
            paid_spin.setSingleStep(500)
            paid_spin.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px;")
            paid_spin.valueChanged.connect(self._recalc_installments_summary)
            self.inst_table.setCellWidget(row_idx, 2, paid_spin)

            # Payment Date
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("dd/MM/yyyy")
            date_edit.setDate(QDate.currentDate())
            date_edit.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px;")
            self.inst_table.setCellWidget(row_idx, 3, date_edit)

            # Mode
            mode_combo = QComboBox()
            mode_combo.addItems(["Cash", "UPI", "Bank Transfer", "Cheque", "Online"])
            mode_combo.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px;")
            self.inst_table.setCellWidget(row_idx, 4, mode_combo)

            # Receipt/Txn Ref
            ref_input = QLineEdit()
            ref_input.setPlaceholderText("Receipt # / UTR")
            ref_input.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px;")
            self.inst_table.setCellWidget(row_idx, 5, ref_input)

            # Remarks
            remarks_input = QLineEdit()
            remarks_input.setStyleSheet("background-color: #181E2C; border: 1px solid #283347; border-radius: 6px; padding: 2px 6px;")
            self.inst_table.setCellWidget(row_idx, 6, remarks_input)

        # Set fixed height to display all 10 rows completely
        self.inst_table.setFixedHeight(36 + (10 * 40) + 4)
        card_layout.addWidget(self.inst_table)

        # Summary Row (Paid vs Balance)
        summary_row = QHBoxLayout()
        summary_row.setSpacing(16)

        self.total_paid_badge = QLabel("Total Paid: ₹0.00")
        self.total_paid_badge.setStyleSheet("font-size: 13px; font-weight: bold; color: #3B82F6; background: #3B82F618; border: 1px solid #3B82F644; border-radius: 8px; padding: 6px 14px;")
        summary_row.addWidget(self.total_paid_badge)

        self.balance_badge = QLabel("Balance Due: ₹0.00")
        self.balance_badge.setStyleSheet("font-size: 13px; font-weight: bold; color: #EF4444; background: #EF444418; border: 1px solid #EF444444; border-radius: 8px; padding: 6px 14px;")
        summary_row.addWidget(self.balance_badge)

        summary_row.addStretch()
        card_layout.addLayout(summary_row)

        # Fee Remarks
        remarks_row = QHBoxLayout()
        remarks_row.setSpacing(10)
        remarks_row.addWidget(QLabel("Fee Remarks:"))
        self.fee_remarks_input = QLineEdit()
        self.fee_remarks_input.setPlaceholderText("e.g. Approved 10% early-bird discount by Director")
        remarks_row.addWidget(self.fee_remarks_input)
        card_layout.addLayout(remarks_row)

        self.content_layout.addWidget(card)

    def _recalc_net_fee(self):
        total = self.total_fee_spin.value()
        disc = self.discount_spin.value()
        net = max(0.0, total - disc)
        self.net_fee_spin.setValue(net)
        self._recalc_installments_summary()

    def _recalc_installments_summary(self):
        net = self.net_fee_spin.value()
        running_due = net
        total_paid = 0.0

        for r in range(10):
            due_spin = self.inst_table.cellWidget(r, 1)
            paid_spin = self.inst_table.cellWidget(r, 2)
            paid_val = paid_spin.value() if paid_spin else 0.0
            total_paid += paid_val

            if due_spin:
                if paid_val > 0 or r == 0:
                    row_due = running_due
                elif running_due > 0 and r > 0:
                    prev_paid_spin = self.inst_table.cellWidget(r - 1, 2)
                    if prev_paid_spin and prev_paid_spin.value() > 0:
                        row_due = running_due
                    else:
                        row_due = 0.0
                else:
                    row_due = 0.0

                due_spin.blockSignals(True)
                due_spin.setValue(row_due)
                due_spin.blockSignals(False)

                running_due = max(0.0, running_due - paid_val)

        bal = max(0.0, net - total_paid)
        self.total_paid_badge.setText(f"Total Paid: ₹{total_paid:,.2f}")
        self.balance_badge.setText(f"Balance Due: ₹{bal:,.2f}")


    def _build_custom_fields_section(self):
        """Dynamic Custom Fields section configured by the institute."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(12)

        title = QLabel("🧩 Additional / Institute Custom Fields")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        defs = StudentController.get_custom_field_definitions("student")
        self.dynamic_widget = DynamicFieldsWidget(defs)
        card_layout.addWidget(self.dynamic_widget)

        self.content_layout.addWidget(card)

    def _build_declaration_section(self):
        """Declaration & Rules Acceptance."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)

        title = QLabel("📝 Declaration & Terms Acceptance")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        self.decl_check = QCheckBox("I confirm that the applicant has agreed to the CADDESK CENTRE declaration and institute terms & conditions.")
        self.decl_check.setChecked(True)
        self.decl_check.setStyleSheet("font-weight: 500; color: #CBD5E1;")
        card_layout.addWidget(self.decl_check)

        self.content_layout.addWidget(card)

    def _populate_data(self):
        """Populate form fields when editing an existing student."""
        s = self.student
        if not s:
            return

        self.id_input.setText(s.id_no or "")
        self.online_check.setChecked(bool(s.is_online))
        self.online_reg_input.setText(s.online_reg_no or "")
        if s.admission_date:
            self.adm_date_edit.setDate(QDate(s.admission_date.year, s.admission_date.month, s.admission_date.day))

        if s.photo_path:
            self._display_photo(s.photo_path)

        self.name_input.setText(s.name or "")
        self.father_name_input.setText(s.father_name or "")
        self.mother_name_input.setText(s.mother_name or "")
        if s.dob:
            self.dob_input.setDate(QDate(s.dob.year, s.dob.month, s.dob.day))
        self.father_occ_input.setText(s.father_occupation or "")
        self.college_input.setText(s.college_school or "")
        self.year_sem_input.setText(s.year_sem or "")
        self.aadhar_input.setText(s.aadhar_no or "")
        self.course_name_input.setText(s.course_name or "")

        self.mobile_input.setText(s.mobile_no or "")
        self.email_input.setText(s.email or "")
        self.father_contact_input.setText(s.father_contact_no or "")
        self.alt_contact_input.setText(s.alternate_contact_no or "")
        self.address_input.setPlainText(s.permanent_address or "")
        self.district_input.setText(s.district or "")
        self.state_input.setText(s.state or "")
        self.pin_input.setText(s.pin_code or "")

        self.total_fee_spin.setValue(s.total_fee or 0.0)
        self.discount_spin.setValue(s.discount_amount or 0.0)
        self.net_fee_spin.setValue(s.net_fee or 0.0)
        self.fee_remarks_input.setText(s.fee_remarks or "")

        self.decl_check.setChecked(bool(s.declaration_agreed))
        
        idx = self.status_combo.findText(s.status or "Active")
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        # Installments
        installments = s.fee_installments or []
        for inst in installments:
            r = inst.installment_no - 1
            if 0 <= r < 10:
                due_spin = self.inst_table.cellWidget(r, 1)
                paid_spin = self.inst_table.cellWidget(r, 2)
                date_edit = self.inst_table.cellWidget(r, 3)
                mode_combo = self.inst_table.cellWidget(r, 4)
                ref_input = self.inst_table.cellWidget(r, 5)
                remarks_input = self.inst_table.cellWidget(r, 6)

                if due_spin: due_spin.setValue(inst.due_amount or 0.0)
                if paid_spin: paid_spin.setValue(inst.paid_amount or 0.0)
                if date_edit and inst.payment_date:
                    date_edit.setDate(QDate(inst.payment_date.year, inst.payment_date.month, inst.payment_date.day))
                if mode_combo and inst.payment_mode:
                    m_idx = mode_combo.findText(inst.payment_mode)
                    if m_idx >= 0: mode_combo.setCurrentIndex(m_idx)
                if ref_input: ref_input.setText(inst.transaction_ref or "")
                if remarks_input: remarks_input.setText(inst.remarks or "")

        self._recalc_installments_summary()

        # Custom Fields
        custom_vals = StudentController.get_student_custom_values(s.id)
        self.dynamic_widget.set_values(custom_vals)

    def _on_save(self):
        """Validate and commit student record."""
        id_no = self.id_input.text().strip()
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()

        if not id_no:
            QMessageBox.warning(self, "Validation Error", "Please provide a valid ID No.")
            self.id_input.setFocus()
            return

        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter the Student's Full Name.")
            self.name_input.setFocus()
            return

        if not mobile:
            QMessageBox.warning(self, "Validation Error", "Please enter Mobile Number.")
            self.mobile_input.setFocus()
            return

        # Handle Photo persistence
        photo_filename = self.selected_photo_path
        if self.temp_photo_file:
            photo_filename = StudentController.save_photo_attachment(self.temp_photo_file)

        # Format Dates
        dob_q = self.dob_input.date()
        dob_val = date(dob_q.year(), dob_q.month(), dob_q.day())

        adm_q = self.adm_date_edit.date()
        adm_val = date(adm_q.year(), adm_q.month(), adm_q.day())

        course_sessions_data = []

        # Collect 10 Installments Data
        fee_installments_data = []
        ordinal_labels = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
        for r in range(10):
            due_spin = self.inst_table.cellWidget(r, 1)
            paid_spin = self.inst_table.cellWidget(r, 2)
            date_edit = self.inst_table.cellWidget(r, 3)
            mode_combo = self.inst_table.cellWidget(r, 4)
            ref_input = self.inst_table.cellWidget(r, 5)
            remarks_input = self.inst_table.cellWidget(r, 6)

            due_amt = due_spin.value() if due_spin else 0.0
            paid_amt = paid_spin.value() if paid_spin else 0.0

            q_dt = date_edit.date() if date_edit else QDate.currentDate()
            pay_dt = date(q_dt.year(), q_dt.month(), q_dt.day())

            fee_installments_data.append({
                "installment_no": r + 1,
                "installment_label": ordinal_labels[r],
                "due_amount": due_amt,
                "paid_amount": paid_amt,
                "due_date": pay_dt,
                "payment_date": pay_dt if paid_amt > 0 else None,
                "payment_mode": mode_combo.currentText() if mode_combo else "Cash",
                "transaction_ref": ref_input.text().strip() if ref_input else None,
                "remarks": remarks_input.text().strip() if remarks_input else None,
            })

        total_fee_val = self.total_fee_spin.value()
        discount_val = self.discount_spin.value()
        net_fee_val = self.net_fee_spin.value()

        # If user left total fee as 0, calculate effective total from installments
        if total_fee_val <= 0:
            first_due = fee_installments_data[0]["due_amount"] if fee_installments_data else 0.0
            sum_paid = sum(inst["paid_amount"] for inst in fee_installments_data)
            if first_due > 0:
                total_fee_val = first_due
                net_fee_val = max(0.0, total_fee_val - discount_val)
            elif sum_paid > 0:
                total_fee_val = sum_paid
                net_fee_val = max(0.0, total_fee_val - discount_val)

        student_data = {
            "id_no": id_no,
            "is_online": self.online_check.isChecked(),
            "online_reg_no": self.online_reg_input.text().strip() if self.online_check.isChecked() else None,
            "photo_path": photo_filename,
            "name": name,
            "father_name": self.father_name_input.text().strip() or None,
            "mother_name": self.mother_name_input.text().strip() or None,
            "dob": dob_val,
            "father_occupation": self.father_occ_input.text().strip() or None,
            "college_school": self.college_input.text().strip() or None,
            "course_name": self.course_name_input.text().strip() or None,
            "year_sem": self.year_sem_input.text().strip() or None,
            "aadhar_no": self.aadhar_input.text().strip() or None,
            "mobile_no": mobile,
            "email": self.email_input.text().strip() or None,
            "father_contact_no": self.father_contact_input.text().strip() or None,
            "alternate_contact_no": self.alt_contact_input.text().strip() or None,
            "permanent_address": self.address_input.toPlainText().strip() or None,
            "district": self.district_input.text().strip() or None,
            "state": self.state_input.text().strip() or None,
            "pin_code": self.pin_input.text().strip() or None,
            "status": self.status_combo.currentText(),
            "admission_date": adm_val,
            "declaration_agreed": self.decl_check.isChecked(),
            "total_fee": total_fee_val,
            "discount_amount": discount_val,
            "net_fee": net_fee_val,
            "fee_remarks": self.fee_remarks_input.text().strip() or None,
        }

        # Collect Custom Field Values
        custom_values = self.dynamic_widget.get_values()

        try:
            if self.is_edit:
                StudentController.update_student(
                    self.student.id,
                    student_data,
                    course_sessions_data,
                    fee_installments_data,
                    custom_values,
                )
            else:
                StudentController.create_student(
                    student_data,
                    course_sessions_data,
                    fee_installments_data,
                    custom_values,
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save student record: {e}")

