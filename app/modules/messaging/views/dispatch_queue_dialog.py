from datetime import datetime
from typing import List, Optional
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.student import Student
from app.modules.messaging.controllers import MessageController


class DispatchQueueDialog(QDialog):
    """Interactive sequential dispatch queue for sending WhatsApp messages to selected students."""

    def __init__(self, students: List[Student], template_text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.students = students
        self.template_text = template_text
        self.current_index = 0
        self.total_count = len(students)

        self.setWindowTitle("WhatsApp Batch Dispatch Queue")
        self.setMinimumSize(680, 580)
        self.resize(740, 620)

        self._build_ui()
        self._load_current_student()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # Header Title & Progress Counter
        h_layout = QHBoxLayout()
        self.title_lbl = QLabel("📢 WhatsApp Batch Dispatcher")
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        h_layout.addWidget(self.title_lbl)

        h_layout.addStretch()

        self.count_badge = QLabel(f"0 of {self.total_count}")
        self.count_badge.setStyleSheet("background-color: #2563EB22; color: #60A5FA; border: 1px solid #2563EB55; border-radius: 12px; font-size: 12px; font-weight: 700; padding: 4px 12px;")
        h_layout.addWidget(self.count_badge)

        main_layout.addLayout(h_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, max(1, self.total_count))
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1E2330;
                border: 1px solid #283042;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Dispatch Method Selector Card
        method_card = QFrame()
        method_card.setStyleSheet("background-color: #161A23; border: 1px solid #283042; border-radius: 8px; padding: 6px 12px;")
        m_layout = QHBoxLayout(method_card)
        m_layout.setContentsMargins(0, 0, 0, 0)
        m_layout.setSpacing(16)

        m_layout.addWidget(QLabel("<b>Dispatch Method:</b>"))

        self.radio_desktop = QRadioButton("🖥️ WhatsApp Desktop App (whatsapp://)")
        self.radio_desktop.setChecked(True)
        m_layout.addWidget(self.radio_desktop)

        self.radio_web = QRadioButton("🌐 WhatsApp Web (web.whatsapp.com)")
        m_layout.addWidget(self.radio_web)

        m_layout.addStretch()
        main_layout.addWidget(method_card)

        # Current Recipient Card
        self.recip_card = QFrame()
        self.recip_card.setStyleSheet("background-color: #1A1F2C; border: 1px solid #334155; border-radius: 8px; padding: 12px;")
        r_layout = QVBoxLayout(self.recip_card)
        r_layout.setSpacing(6)

        self.st_name_lbl = QLabel("Recipient: Pawan Shekhawat")
        self.st_name_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #38BDF8;")
        r_layout.addWidget(self.st_name_lbl)

        self.st_meta_lbl = QLabel("ID: CD-2026-0001 | Mobile: 9876543210 | Course: AutoCAD | Balance: ₹10,000")
        self.st_meta_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        r_layout.addWidget(self.st_meta_lbl)

        main_layout.addWidget(self.recip_card)

        # Live Rendered Message Preview Box
        msg_box_title = QLabel("<b>Personalized Message to Send:</b>")
        msg_box_title.setStyleSheet("font-size: 12px; color: #E2E8F0;")
        main_layout.addWidget(msg_box_title)

        self.msg_preview = QTextEdit()
        self.msg_preview.setReadOnly(True)
        self.msg_preview.setMinimumHeight(110)
        self.msg_preview.setStyleSheet("background-color: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 10px; font-size: 12px; color: #F1F5F9;")
        main_layout.addWidget(self.msg_preview)

        # Action Buttons Row
        act_row = QHBoxLayout()
        act_row.setSpacing(10)

        self.skip_btn = QPushButton("⏭️ Skip Student")
        self.skip_btn.setStyleSheet("background-color: #334155; color: #F1F5F9; border: 1px solid #475569; border-radius: 6px; padding: 8px 14px; font-weight: 600;")
        self.skip_btn.clicked.connect(self._on_skip)
        act_row.addWidget(self.skip_btn)

        act_row.addStretch()

        self.send_btn = QPushButton("🚀 Open in WhatsApp & Next (Enter)")
        self.send_btn.setObjectName("primaryBtn")
        self.send_btn.setStyleSheet("background-color: #059669; color: #FFFFFF; border: 1px solid #047857; border-radius: 6px; padding: 9px 20px; font-size: 13px; font-weight: 700;")
        self.send_btn.clicked.connect(self._on_send_and_next)
        act_row.addWidget(self.send_btn)

        main_layout.addLayout(act_row)

        # Queue Activity Log Table
        log_title = QLabel("<b>Dispatch History Log:</b>")
        log_title.setStyleSheet("font-size: 11px; color: #64748B; margin-top: 4px;")
        main_layout.addWidget(log_title)

        self.log_table = QTableWidget(0, 4)
        self.log_table.setHorizontalHeaderLabels(["Student Name", "Mobile Number", "Status", "Time"])
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.setFixedHeight(120)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.log_table)

    def _load_current_student(self):
        if self.current_index >= self.total_count:
            self._on_queue_finished()
            return

        s = self.students[self.current_index]
        self.count_badge.setText(f"{self.current_index + 1} of {self.total_count}")
        self.progress_bar.setValue(self.current_index)

        self.st_name_lbl.setText(f"👤 Recipient: {s.name}")
        last_pay = f"Last Paid: {s.last_payment_summary}" if s.last_payment_date else "No prior payments"
        self.st_meta_lbl.setText(f"ID: {s.id_no} &nbsp;|&nbsp; Mob: <b>{s.mobile_no}</b> &nbsp;|&nbsp; Course: {s.course_name or 'N/A'} &nbsp;|&nbsp; Bal: ₹{s.balance_due:,.0f} &nbsp;|&nbsp; {last_pay}")

        # Render message for this student
        rendered = MessageController.render_message(self.template_text, s, randomize_spintax=True)
        self.msg_preview.setPlainText(rendered)

    def _on_send_and_next(self):
        if self.current_index >= self.total_count:
            return

        s = self.students[self.current_index]
        msg = self.msg_preview.toPlainText().strip()
        use_desktop = self.radio_desktop.isChecked()

        # Build WhatsApp link and trigger default OS handler
        url_str = MessageController.build_whatsapp_url(s.mobile_no, msg, use_desktop_app=use_desktop)
        QDesktopServices.openUrl(QUrl(url_str))

        # Add to log
        self._add_log_entry(s.name, s.mobile_no, "✅ Opened in WhatsApp", "#10B981")

        # Move to next
        self.current_index += 1
        self._load_current_student()

    def _on_skip(self):
        if self.current_index >= self.total_count:
            return
        s = self.students[self.current_index]
        self._add_log_entry(s.name, s.mobile_no, "⏭️ Skipped", "#F59E0B")
        self.current_index += 1
        self._load_current_student()

    def _add_log_entry(self, name: str, mobile: str, status_text: str, color_hex: str):
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        item_name = QTableWidgetItem(name)
        item_mob = QTableWidgetItem(mobile)
        item_status = QTableWidgetItem(status_text)
        item_status.setForeground(Qt.white)
        item_time = QTableWidgetItem(datetime.now().strftime("%I:%M:%S %p"))

        self.log_table.setItem(row, 0, item_name)
        self.log_table.setItem(row, 1, item_mob)
        self.log_table.setItem(row, 2, item_status)
        self.log_table.setItem(row, 3, item_time)
        self.log_table.scrollToBottom()

    def _on_queue_finished(self):
        self.progress_bar.setValue(self.total_count)
        self.count_badge.setText(f"Completed ({self.total_count}/{self.total_count})")
        self.st_name_lbl.setText("🎉 All selected student messages processed!")
        self.st_meta_lbl.setText("Queue execution finished.")
        self.msg_preview.setPlainText("All messages in this batch have been opened/dispatched in WhatsApp.")
        self.send_btn.setEnabled(False)
        self.skip_btn.setText("Close Queue")
        self.skip_btn.clicked.disconnect()
        self.skip_btn.clicked.connect(self.accept)

    def keyPressEvent(self, event):
        """Allow pressing Enter / Return to quickly trigger Send & Next."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.send_btn.isEnabled():
                self._on_send_and_next()
                return
        super().keyPressEvent(event)
