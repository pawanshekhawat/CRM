from datetime import date
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


class StatusBadgeComboBox(QComboBox):
    """Inline interactive Status dropdown badge that instantly persists status changes to SQLite DB."""

    def __init__(self, student_id: str, current_status: str, on_change_callback, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.on_change_callback = on_change_callback
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(28)
        self.setFixedWidth(130)

        self.addItems(["Active", "Completed", "Dropout"])

        # Block signals during initial setup
        self.blockSignals(True)
        idx = self.findText(current_status if current_status in ["Active", "Completed", "Dropout"] else "Active")
        if idx >= 0:
            self.setCurrentIndex(idx)
        self.blockSignals(False)

        self._apply_badge_style(self.currentText())
        self.currentTextChanged.connect(self._handle_status_change)

    def _apply_badge_style(self, status: str):
        if status == "Active":
            bg = "#10B9811C"
            border = "#10B98177"
            color = "#10B981"
            arrow = "#10B981"
        elif status == "Completed":
            bg = "#3B82F61C"
            border = "#3B82F677"
            color = "#3B82F6"
            arrow = "#3B82F6"
        else:  # Dropout
            bg = "#71717A24"
            border = "#71717A77"
            color = "#A1A1AA"
            arrow = "#A1A1AA"

        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: 14px;
                padding: 0px 24px 0px 14px;
                margin: 0px;
                font-size: 12px;
                font-weight: 700;
                min-height: 26px;
                max-height: 28px;
            }}
            QComboBox:hover {{
                border: 1px solid {color};
                background-color: {bg};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 22px;
                border-left: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {arrow};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #0F172A;
                color: #F8FAFC;
                border: 1px solid #334155;
                selection-background-color: #1E293B;
                selection-color: #38BDF8;
                padding: 6px;
                border-radius: 8px;
                outline: none;
                font-size: 12px;
                font-weight: 600;
                min-width: 130px;
            }}
            QComboBox QAbstractItemView::item {{
                height: 28px;
                padding-left: 10px;
                border-radius: 4px;
            }}
        """)

    def _handle_status_change(self, new_status: str):
        self._apply_badge_style(new_status)
        if self.on_change_callback:
            self.on_change_callback(self.student_id, new_status)


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
        self.search_bar.setMinimumWidth(200)
        toolbar.addWidget(self.search_bar, 2)

        # Status Filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Active", "Completed", "Dropout"])
        self.status_filter.setMinimumWidth(125)
        self.status_filter.currentTextChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.status_filter, 0)

        # Fee Filter
        self.fee_filter = QComboBox()
        self.fee_filter.addItems(["All Fees", "Paid", "Partial", "Pending", "No Fee"])
        self.fee_filter.setMinimumWidth(115)
        self.fee_filter.currentTextChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.fee_filter, 0)

        # Sort By Filter
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Sort: Default (ID)",
            "Sort: Name (A-Z)",
            "Sort: Name (Z-A)",
            "Sort: Courses",
            "Sort: Last Paid (Recent)",
            "Sort: Last Paid (Oldest)",
            "Sort: Fee (Pending)",
            "Sort: Active Status",
            "Sort: Latest Admissions",
        ])
        self.sort_combo.setMinimumWidth(190)
        self.sort_combo.setToolTip("Sort students by Name, Course, Last Fee Paid, Active Status, or ID")
        self.sort_combo.currentTextChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.sort_combo, 0)

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
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Student Name", "Contact Number", "Course Enrolled", "Last Fee Paid", "Fee Status", "Status", "Actions"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) # Student Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Contact Number
        header.setSectionResizeMode(2, QHeaderView.Stretch) # Course Enrolled
        header.setSectionResizeMode(3, QHeaderView.Fixed) # Last Fee Paid
        self.table.setColumnWidth(3, 175) # Dedicated 175px for "📅 23 Jul 2026 / ⏱️ 53d ago"
        header.setSectionResizeMode(4, QHeaderView.Fixed) # Fee Status
        self.table.setColumnWidth(4, 185) # Dedicated 185px for Fee Status badge
        header.setSectionResizeMode(5, QHeaderView.Fixed) # Status
        self.table.setColumnWidth(5, 145) # Dedicated 145px for Status dropdown badge
        header.setSectionResizeMode(6, QHeaderView.Fixed) # Actions
        self.table.setColumnWidth(6, 215) # Dedicated 215px for WhatsApp and View buttons

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self._on_row_double_click)
        header.sectionClicked.connect(self._on_header_clicked)

        parent_layout.addWidget(self.table)

    def _on_header_clicked(self, logical_index: int):
        """Allow clicking on table headers to quickly change sort order."""
        if logical_index == 0:  # Student Name
            if self.sort_combo.currentText() == "Sort: Name (A-Z)":
                self.sort_combo.setCurrentText("Sort: Name (Z-A)")
            else:
                self.sort_combo.setCurrentText("Sort: Name (A-Z)")
        elif logical_index == 2:  # Course Enrolled
            self.sort_combo.setCurrentText("Sort: Courses")
        elif logical_index == 3:  # Last Fee Paid
            if self.sort_combo.currentText() == "Sort: Last Paid (Recent)":
                self.sort_combo.setCurrentText("Sort: Last Paid (Oldest)")
            else:
                self.sort_combo.setCurrentText("Sort: Last Paid (Recent)")
        elif logical_index == 4:  # Fee Status
            self.sort_combo.setCurrentText("Sort: Fee (Pending)")
        elif logical_index == 5:  # Status
            self.sort_combo.setCurrentText("Sort: Active Status")

    def refresh_data(self):
        """Fetch filtered and sorted students and update table and KPI cards."""
        query = self.search_bar.text()
        status = self.status_filter.currentText()
        fee = self.fee_filter.currentText()
        sort_by = self.sort_combo.currentText()

        status_val = None if status == "All Status" else status
        fee_val = None if fee == "All Fees" else fee

        students = StudentController.get_all_students(
            search_query=query,
            status_filter=status_val,
            fee_filter=fee_val,
            sort_by=sort_by,
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

            # 4. Last Fee Paid Widget (Next to Course Enrolled)
            last_paid_widget = QWidget()
            last_paid_widget.setStyleSheet("background: transparent;")
            lp_layout = QVBoxLayout(last_paid_widget)
            lp_layout.setContentsMargins(6, 4, 6, 4)
            lp_layout.setSpacing(2)
            lp_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            last_dt = s.last_payment_date
            days_ago = s.days_since_last_payment
            last_inst = s.latest_paid_installment

            if last_dt is not None and days_ago is not None:
                dt_str = last_dt.strftime("%d %b %Y")
                if days_ago == 0:
                    days_text = "Today"
                    badge_color = "#10B981"
                elif days_ago == 1:
                    days_text = "Yesterday"
                    badge_color = "#10B981"
                elif days_ago <= 30:
                    days_text = f"{days_ago} days ago"
                    badge_color = "#34D399"
                elif days_ago <= 60:
                    days_text = f"{days_ago} days ago"
                    badge_color = "#F59E0B"
                else:
                    days_text = f"{days_ago} days ago"
                    badge_color = "#F87171"

                dt_lbl = QLabel(f"📅 {dt_str}")
                dt_lbl.setStyleSheet("color: #F1F5F9; font-size: 12px; font-weight: 600;")

                days_lbl = QLabel(f"⏱️ {days_text}")
                days_lbl.setStyleSheet(f"color: {badge_color}; font-size: 11px; font-weight: 600;")

                lp_layout.addWidget(dt_lbl)
                lp_layout.addWidget(days_lbl)

                inst_label = last_inst.installment_label if last_inst else "N/A"
                paid_amt = last_inst.paid_amount if last_inst else 0.0
                mode = last_inst.payment_mode if (last_inst and last_inst.payment_mode) else "Cash/UPI"

                last_paid_widget.setToolTip(
                    f"Last Payment: ₹{paid_amt:,.2f} ({inst_label} Installment)\n"
                    f"Date: {dt_str}\n"
                    f"Time Elapsed: {days_ago} days ago\n"
                    f"Payment Mode: {mode}\n"
                    f"Total Paid so far: ₹{s.total_paid:,.2f} | Balance: ₹{s.balance_due:,.2f}"
                )
            else:
                if s.fee_status == "No Fee" or s.effective_net_fee == 0:
                    dt_lbl = QLabel("—")
                    dt_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
                    days_lbl = QLabel("No Fee")
                    days_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
                    last_paid_widget.setToolTip("No fee configured for this student")
                else:
                    adm_days = (date.today() - s.admission_date).days if s.admission_date else 0
                    dt_lbl = QLabel("❌ Unpaid")
                    dt_lbl.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 600;")
                    days_lbl = QLabel(f"{adm_days}d since adm.")
                    days_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
                    last_paid_widget.setToolTip(
                        f"No payments received yet.\n"
                        f"Admission Date: {s.admission_date.strftime('%d %b %Y') if s.admission_date else 'N/A'} ({adm_days} days ago)\n"
                        f"Total Net Fee: ₹{s.net_fee:,.2f}"
                    )

                lp_layout.addWidget(dt_lbl)
                lp_layout.addWidget(days_lbl)

            last_paid_item = QTableWidgetItem()
            last_paid_item.setData(Qt.UserRole, days_ago if days_ago is not None else 999999)
            last_paid_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            # 5. Fee Status Badge Widget
            fee_status_widget = QWidget()
            fee_status_widget.setStyleSheet("background: transparent;")
            f_layout = QHBoxLayout(fee_status_widget)
            f_layout.setContentsMargins(0, 0, 0, 0)
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

            # 6. Inline Editable Status Badge Dropdown
            status_widget = QWidget()
            status_widget.setStyleSheet("background: transparent;")
            st_layout = QHBoxLayout(status_widget)
            st_layout.setContentsMargins(0, 0, 0, 0)
            st_layout.setAlignment(Qt.AlignCenter)

            status_combo = StatusBadgeComboBox(
                student_id=s.id,
                current_status=s.status or "Active",
                on_change_callback=self._on_inline_status_changed,
                parent=self,
            )
            status_combo.setToolTip(f"Click to change status for {s.name} (instantly saved to DB)")
            st_layout.addWidget(status_combo)

            # 7. Actions Widget (WhatsApp + View)
            act_widget = QWidget()
            act_widget.setStyleSheet("background: transparent;")
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(0, 0, 0, 0)
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
            self.table.setItem(row_idx, 3, last_paid_item)
            self.table.setCellWidget(row_idx, 3, last_paid_widget)
            self.table.setCellWidget(row_idx, 4, fee_status_widget)
            self.table.setCellWidget(row_idx, 5, status_widget)
            self.table.setCellWidget(row_idx, 6, act_widget)

    def _on_inline_status_changed(self, student_id: str, new_status: str):
        """Immediately updates student status in SQLite DB and updates dashboard stats."""
        try:
            success = StudentController.update_student_status(student_id, new_status)
            if success:
                self._update_kpi_metrics()
                # Update in-memory reference
                for st in getattr(self, "current_students", []):
                    if st.id == student_id:
                        st.status = new_status
                        break
        except Exception as e:
            QMessageBox.critical(self, "Status Update Error", f"Failed to save status: {e}")

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
