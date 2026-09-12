from typing import List, Optional
from PySide6.QtCore import Qt, QUrl, QRectF
from PySide6.QtGui import QDesktopServices, QPixmap, QPainter, QPainterPath, QColor, QFont, QBrush
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.config import PHOTOS_DIR
from app.models.student import Student
from app.modules.students.controllers import StudentController
from app.modules.students.reports import ReportGenerator
from app.modules.students.views.custom_fields_dialog import CustomFieldsDialog
from app.modules.students.views.student_detail_view import StudentDetailView
from app.modules.students.views.student_form_dialog import StudentFormDialog
from app.ui.widgets.search_bar import SearchBar
from app.ui.widgets.stat_card import StatCard


def create_student_avatar_pixmap(photo_path_name: Optional[str], student_name: str, size: int = 34) -> QPixmap:
    """Renders a rounded square / squircle avatar thumbnail from student photo or dynamic stylish initials."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    # Rounded path (radius 8 for squircle look)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size, size, 8, 8)
    painter.setClipPath(path)

    photo_loaded = False
    if photo_path_name:
        p_file = PHOTOS_DIR / photo_path_name
        if p_file.exists():
            orig = QPixmap(str(p_file))
            if not orig.isNull():
                # Scale to fill and crop center
                scaled = orig.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                x_off = max(0, (scaled.width() - size) // 2)
                y_off = max(0, (scaled.height() - size) // 2)
                painter.drawPixmap(0, 0, scaled, x_off, y_off, size, size)
                photo_loaded = True

    if not photo_loaded:
        # Dynamic pleasant color palette for initials
        palette = [
            ("#2563EB", "#1D4ED8"),  # Royal Blue
            ("#7C3AED", "#6D28D9"),  # Violet
            ("#059669", "#047857"),  # Emerald
            ("#D97706", "#B45309"),  # Amber
            ("#DB2777", "#BE185D"),  # Pink
            ("#0891B2", "#0E7490"),  # Cyan
            ("#4F46E5", "#4338CA"),  # Indigo
        ]
        color_idx = sum(ord(c) for c in (student_name or "S")) % len(palette)
        bg_col, _ = palette[color_idx]

        painter.setBrush(QBrush(QColor(bg_col)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, size, size, 8, 8)

        # Generate initials
        parts = (student_name or "").strip().split()
        if len(parts) >= 2:
            initials = f"{parts[0][0]}{parts[1][0]}".upper()
        elif len(parts) == 1 and parts[0]:
            initials = parts[0][:2].upper()
        else:
            initials = "ST"

        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, size, size), Qt.AlignCenter, initials)

    painter.end()
    return pixmap


class StudentListView(QWidget):
    """Main Student Directory & Admission Management view."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # 1. Top KPI Metric Cards Row
        self._build_stat_cards(main_layout)

        # 2. Action & Filter Bar
        self._build_toolbar(main_layout)

        # 3. Main Student Data Table
        self._build_table(main_layout)

        # Load initial data
        self.refresh_data()

    def _build_stat_cards(self, parent_layout: QVBoxLayout):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_total = StatCard("Total Enrolled", "0", "All time admissions", "🎓", "#3B82F6")
        self.card_active = StatCard("Active Students", "0", "Currently pursuing", "🟢", "#10B981")
        self.card_collected = StatCard("Fees Collected", "₹0", "Total installments paid", "💰", "#059669")
        self.card_pending = StatCard("Pending Dues", "₹0", "Balance to collect", "⏳", "#EF4444")

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_active)
        cards_layout.addWidget(self.card_collected)
        cards_layout.addWidget(self.card_pending)

        parent_layout.addLayout(cards_layout)

    def _build_toolbar(self, parent_layout: QVBoxLayout):
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Search Bar
        self.search_bar = SearchBar(placeholder="Search by Name, Mobile, Course, ID, College...")
        self.search_bar.searched.connect(self._on_filter_changed)
        toolbar.addWidget(self.search_bar, 3)

        # Status Filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Active", "Completed", "Dropped", "Inquiry"])
        self.status_filter.currentTextChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.status_filter, 1)

        # Fee Filter
        self.fee_filter = QComboBox()
        self.fee_filter.addItems(["All Fees", "Paid", "Partial", "Pending", "No Fee"])
        self.fee_filter.currentTextChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.fee_filter, 1)

        # Custom Fields Button
        custom_fields_btn = QPushButton("⚙️ Custom Fields")
        custom_fields_btn.setToolTip("Configure dynamic custom inputs on the fly")
        custom_fields_btn.clicked.connect(self._open_custom_fields_dialog)
        toolbar.addWidget(custom_fields_btn)

        # Export Excel Button
        export_btn = QPushButton("📊 Export")
        export_btn.clicked.connect(self._export_excel)
        toolbar.addWidget(export_btn)

        # New Student Button
        new_btn = QPushButton("+ New Admission")
        new_btn.setObjectName("primaryBtn")
        new_btn.clicked.connect(self._open_new_student_dialog)
        toolbar.addWidget(new_btn)

        parent_layout.addLayout(toolbar)

    def _build_table(self, parent_layout: QVBoxLayout):
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Student Name", "Contact Number", "Course Enrolled", "Fee Status", "Actions"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 195) # Dedicated 195px so full text "● Partial (Bal: ₹35,000)" never clips
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 225) # Dedicated 225px for WhatsApp and View buttons

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self._on_row_double_click)

        parent_layout.addWidget(self.table)

    def refresh_data(self):
        """Fetch filtered students and update table and KPI cards."""
        query = self.search_bar.text()
        status = self.status_filter.currentText()
        fee = self.fee_filter.currentText()

        status_val = None if status == "All Status" else status
        fee_val = None if fee == "All Fees" else fee

        students = StudentController.get_all_students(
            search_query=query,
            status_filter=status_val,
            fee_filter=fee_val,
        )

        self._populate_table(students)
        self._update_kpi_metrics()

    def _populate_table(self, students: List[Student]):
        self.table.setRowCount(0)
        self.current_students = students

        for row_idx, s in enumerate(students):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 50)

            # 1. Student Name with Avatar Thumbnail
            name_widget = QWidget()
            name_widget.setStyleSheet("background: transparent;")
            n_layout = QHBoxLayout(name_widget)
            n_layout.setContentsMargins(8, 2, 8, 2)
            n_layout.setSpacing(10)
            n_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Avatar label
            avatar_lbl = QLabel()
            avatar_lbl.setFixedSize(34, 34)
            avatar_lbl.setPixmap(create_student_avatar_pixmap(s.photo_path, s.name, size=34))
            avatar_lbl.setStyleSheet("border-radius: 8px; border: 1px solid #334155; background-color: #1E293B;")
            avatar_lbl.setAlignment(Qt.AlignCenter)
            n_layout.addWidget(avatar_lbl)

            # Name + ID Stack
            text_layout = QVBoxLayout()
            text_layout.setSpacing(1)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setAlignment(Qt.AlignVCenter)

            name_lbl = QLabel(s.name)
            name_lbl.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 13px;")
            text_layout.addWidget(name_lbl)

            id_lbl = QLabel(f"ID: {s.id_no}")
            id_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            text_layout.addWidget(id_lbl)

            n_layout.addLayout(text_layout)

            name_widget.setToolTip(f"ID: {s.id_no}\nFather: {s.father_name or 'N/A'}\nCollege: {s.college_school or 'N/A'}")
            name_widget.mouseDoubleClickEvent = lambda event, sid=s.id: self._open_detail_view(sid)
            name_item = QTableWidgetItem()
            name_item.setData(Qt.UserRole, s.name)
            name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            # 2. Contact Number
            mobile_item = QTableWidgetItem(s.mobile_no)
            mobile_item.setTextAlignment(Qt.AlignCenter)
            mobile_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            # 3. Course Enrolled
            course_item = QTableWidgetItem(s.course_name or "-")
            course_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            # 4. Fee Status Badge Widget
            fee_status_widget = QWidget()
            fee_status_widget.setStyleSheet("background: transparent;")
            f_layout = QHBoxLayout(fee_status_widget)
            f_layout.setContentsMargins(6, 4, 6, 4)
            f_layout.setAlignment(Qt.AlignCenter)

            fee_status = s.fee_status
            if fee_status == "Paid":
                fee_col = "#10B981"
                fee_text = "● Paid"
            elif fee_status == "Partial":
                fee_col = "#F59E0B"
                fee_text = f"● Partial (Bal: ₹{s.balance_due:,.0f})"
            elif fee_status == "Pending":
                fee_col = "#EF4444"
                fee_text = f"● Pending (Due: ₹{s.balance_due:,.0f})"
            else:
                fee_col = "#64748B"
                fee_text = "● No Fee"

            fee_badge = QLabel(f" {fee_text} ")
            fee_badge.setAlignment(Qt.AlignCenter)
            fee_badge.setStyleSheet(f"""
                background-color: {fee_col}18;
                color: {fee_col};
                border: 1px solid {fee_col}66;
                border-radius: 12px;
                font-size: 11.5px;
                font-weight: 700;
                padding: 4px 12px;
                min-height: 20px;
            """)
            fee_badge.setToolTip(f"Net Fee: ₹{s.net_fee:,.2f} | Total Paid: ₹{s.total_paid:,.2f} | Balance: ₹{s.balance_due:,.2f}")
            f_layout.addWidget(fee_badge)


            # 5. Actions Widget (WhatsApp + View)
            act_widget = QWidget()
            act_widget.setStyleSheet("background: transparent;")
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(6, 4, 6, 4)
            act_layout.setSpacing(8)
            act_layout.setAlignment(Qt.AlignCenter)

            # WhatsApp Action Button
            wa_btn = QPushButton("💬 WhatsApp")
            wa_btn.setMinimumWidth(98)
            wa_btn.setStyleSheet("""
                QPushButton {
                    background-color: #059669;
                    color: #FFFFFF;
                    border: 1px solid #047857;
                    border-radius: 6px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #10B981;
                    border-color: #059669;
                }
                QPushButton:pressed {
                    background-color: #047857;
                }
            """)
            wa_btn.setToolTip(f"Send WhatsApp message to {s.name} ({s.mobile_no})")
            wa_btn.clicked.connect(lambda checked=False, mob=s.mobile_no, name=s.name: self._open_whatsapp(mob, name))
            act_layout.addWidget(wa_btn)

            # View Profile Button
            view_btn = QPushButton("👁️ View")
            view_btn.setMinimumWidth(76)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    border: 1px solid #1D4ED8;
                    border-radius: 6px;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #3B82F6;
                    border-color: #2563EB;
                }
                QPushButton:pressed {
                    background-color: #1D4ED8;
                }
            """)
            view_btn.setToolTip(f"View complete profile, fee ledger, and print slip for {s.name}")
            view_btn.clicked.connect(lambda checked=False, sid=s.id: self._open_detail_view(sid))
            act_layout.addWidget(view_btn)

            # Set table items
            self.table.setItem(row_idx, 0, name_item)
            self.table.setCellWidget(row_idx, 0, name_widget)
            self.table.setItem(row_idx, 1, mobile_item)
            self.table.setItem(row_idx, 2, course_item)
            self.table.setCellWidget(row_idx, 3, fee_status_widget)
            self.table.setCellWidget(row_idx, 4, act_widget)

    def _open_whatsapp(self, mobile_no: str, student_name: str):
        """Opens WhatsApp application with the student's phone number."""
        clean_digits = "".join(c for c in (mobile_no or "") if c.isdigit())
        if not clean_digits:
            QMessageBox.warning(self, "Invalid Phone Number", f"No valid mobile number found for {student_name}.")
            return

        # Prepend Indian country code (91) if 10-digit number
        if len(clean_digits) == 10:
            clean_digits = "91" + clean_digits

        # Attempt to open native WhatsApp application URI
        wa_uri = f"whatsapp://send?phone={clean_digits}"
        opened = QDesktopServices.openUrl(QUrl(wa_uri))
        
        # Fallback to web link if native scheme doesn't trigger
        if not opened:
            QDesktopServices.openUrl(QUrl(f"https://wa.me/{clean_digits}"))

    def _update_kpi_metrics(self):
        metrics = StudentController.get_dashboard_metrics()
        
        def format_currency(val: float) -> str:
            if val >= 10000000:
                return f"₹{val/10000000:.2f}Cr"
            elif val >= 100000:
                return f"₹{val/100000:.2f}L"
            return f"₹{val:,.0f}"

        self.card_total.set_value(str(metrics["total_students"]))
        self.card_active.set_value(str(metrics["active_students"]))
        self.card_collected.set_value(format_currency(metrics["total_paid"]))
        self.card_pending.set_value(format_currency(metrics["balance_due"]))

    def _on_filter_changed(self):
        self.refresh_data()

    def _on_row_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self.current_students):
            student = self.current_students[row]
            self._open_detail_view(student.id)

    def _open_new_student_dialog(self):
        dlg = StudentFormDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_data()

    def _open_detail_view(self, student_id: str):
        dlg = StudentDetailView(student_id=student_id, parent=self)
        dlg.student_updated.connect(self.refresh_data)
        dlg.exec()

    def _open_custom_fields_dialog(self):
        dlg = CustomFieldsDialog(parent=self)
        dlg.exec()

    def _export_excel(self):
        try:
            students = StudentController.get_all_students()
            path = ReportGenerator.export_students_to_excel(students)
            QMessageBox.information(self, "Export Complete", f"Students exported to Excel successfully:\n{path}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
