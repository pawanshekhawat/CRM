import html
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
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

ASSETS_DIR = Path(__file__).parent.parent / "assets"
BG_IMAGE_PATH = ASSETS_DIR / "whatsapp_bg.png"


class WhatsAppChatCanvas(QWidget):
    """Custom canvas that tiles the authentic dark WhatsApp doodle wallpaper."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.bg_pixmap: Optional[QPixmap] = None
        if BG_IMAGE_PATH.exists():
            self.bg_pixmap = QPixmap(str(BG_IMAGE_PATH))

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            painter.drawTiledPixmap(self.rect(), self.bg_pixmap)
        else:
            painter.fillRect(self.rect(), QColor("#0B141A"))


class WhatsAppChatPreviewWidget(QFrame):
    """
    Ultra-realistic WhatsApp Web chat interface simulator.
    Renders the authentic top contact header, tiled doodle wallpaper canvas,
    green outgoing chat bubble with timestamp + double ticks, and WhatsApp input bar.
    """
    send_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("whatsappChatCard")
        self.setStyleSheet("""
            QFrame#whatsappChatCard {
                background-color: #111B21;
                border: 1px solid #1F2C34;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Top Contact Header Bar (WhatsApp Web style)
        header_bar = QFrame()
        header_bar.setFixedHeight(46)
        header_bar.setStyleSheet("""
            QFrame {
                background-color: #1F2C34;
                border-top-left-radius: 9px;
                border-top-right-radius: 9px;
                border-bottom: 1px solid #222E35;
            }
            QLabel {
                background: transparent;
                background-color: transparent;
            }
        """)
        h_layout = QHBoxLayout(header_bar)
        h_layout.setContentsMargins(12, 4, 12, 4)
        h_layout.setSpacing(10)

        # Avatar Circle
        self.avatar_lbl = QLabel("SB")
        self.avatar_lbl.setFixedSize(32, 32)
        self.avatar_lbl.setAlignment(Qt.AlignCenter)
        self.avatar_lbl.setStyleSheet("""
            background-color: #00A884;
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 700;
            border-radius: 16px;
        """)
        h_layout.addWidget(self.avatar_lbl)

        # Contact Info Column
        info_col = QVBoxLayout()
        info_col.setSpacing(1)
        info_col.setAlignment(Qt.AlignVCenter)

        self.contact_name_lbl = QLabel("Shivkant Batu")
        self.contact_name_lbl.setStyleSheet("background: transparent; color: #E9EDEF; font-size: 13px; font-weight: 700;")
        info_col.addWidget(self.contact_name_lbl)

        self.contact_status_lbl = QLabel("+91 9828965484 • Student")
        self.contact_status_lbl.setStyleSheet("background: transparent; color: #8696A0; font-size: 10.5px;")
        info_col.addWidget(self.contact_status_lbl)
        h_layout.addLayout(info_col, 1)

        # Top Right Badges / Icons
        self.char_badge = QLabel("0 chars")
        self.char_badge.setStyleSheet("color: #8696A0; font-size: 11px; background-color: #111B21; border-radius: 4px; padding: 2px 6px;")
        h_layout.addWidget(self.char_badge)

        icons_lbl = QLabel("🔍  ⋮")
        icons_lbl.setStyleSheet("background: transparent; color: #AEBAC1; font-size: 13px; margin-left: 6px;")
        h_layout.addWidget(icons_lbl)

        layout.addWidget(header_bar)

        # 2. Chat Canvas with Tiled Doodle Wallpaper
        self.canvas = WhatsAppChatCanvas(self)
        canvas_layout = QVBoxLayout(self.canvas)
        canvas_layout.setContentsMargins(14, 10, 14, 10)
        canvas_layout.setSpacing(8)

        # Date Badge (Centered)
        date_row = QHBoxLayout()
        date_row.addStretch()
        date_pill = QLabel("TODAY")
        date_pill.setStyleSheet("background-color: #182229; color: #8696A0; font-size: 10px; font-weight: 600; padding: 3px 10px; border-radius: 6px;")
        date_row.addWidget(date_pill)
        date_row.addStretch()
        canvas_layout.addLayout(date_row)

        # Outgoing WhatsApp Message Bubble (Right Aligned)
        bubble_row = QHBoxLayout()
        bubble_row.addStretch(1)

        self.bubble_frame = QFrame()
        self.bubble_frame.setObjectName("msgBubble")
        self.bubble_frame.setMaximumWidth(440)
        self.bubble_frame.setStyleSheet("""
            QFrame#msgBubble {
                background-color: #005C4B;
                border-radius: 8px;
                border-top-right-radius: 2px;
            }
            QFrame#msgBubble QLabel {
                background: transparent;
                background-color: transparent;
            }
        """)
        b_layout = QVBoxLayout(self.bubble_frame)
        b_layout.setContentsMargins(12, 9, 12, 7)
        b_layout.setSpacing(4)

        self.msg_text_lbl = QLabel("Select a student to see the live WhatsApp message preview...")
        self.msg_text_lbl.setWordWrap(True)
        self.msg_text_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.msg_text_lbl.setStyleSheet("""
            QLabel {
                background: transparent;
                background-color: transparent;
                color: #E9EDEF;
                font-size: 12.5px;
                line-height: 1.45;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
        """)
        b_layout.addWidget(self.msg_text_lbl)

        # Bubble Footer: Timestamp & Read Receipts
        foot_row = QHBoxLayout()
        foot_row.setSpacing(4)
        foot_row.addStretch()

        now_str = datetime.now().strftime("%I:%M %p").lstrip("0")
        self.time_lbl = QLabel(now_str)
        self.time_lbl.setStyleSheet("background: transparent; background-color: transparent; color: #8696A0; font-size: 10px;")
        foot_row.addWidget(self.time_lbl)

        ticks_lbl = QLabel("✓✓")
        ticks_lbl.setStyleSheet("background: transparent; background-color: transparent; color: #53BDEB; font-size: 11px; font-weight: bold;")
        foot_row.addWidget(ticks_lbl)

        b_layout.addLayout(foot_row)
        bubble_row.addWidget(self.bubble_frame, 4)
        canvas_layout.addLayout(bubble_row)

        canvas_layout.addStretch(1)
        layout.addWidget(self.canvas, 1)

        # 3. Bottom WhatsApp Input Bar (WhatsApp Web style)
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(44)
        bottom_bar.setStyleSheet("""
            QFrame {
                background-color: #1F2C34;
                border-bottom-left-radius: 9px;
                border-bottom-right-radius: 9px;
                border-top: 1px solid #222E35;
            }
            QLabel {
                background: transparent;
                background-color: transparent;
            }
        """)
        bot_layout = QHBoxLayout(bottom_bar)
        bot_layout.setContentsMargins(10, 4, 10, 4)
        bot_layout.setSpacing(8)

        btn_plus = QLabel("+")
        btn_plus.setStyleSheet("background: transparent; color: #8696A0; font-size: 18px; font-weight: 300;")
        bot_layout.addWidget(btn_plus)

        btn_emoji = QLabel("😀")
        btn_emoji.setStyleSheet("background: transparent; font-size: 14px;")
        bot_layout.addWidget(btn_emoji)

        # Input Capsule
        input_pill = QFrame()
        input_pill.setStyleSheet("""
            QFrame {
                background-color: #2A3942;
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
                background-color: transparent;
                color: #8696A0;
                font-size: 11.5px;
            }
        """)
        ip_layout = QHBoxLayout(input_pill)
        ip_layout.setContentsMargins(10, 2, 10, 2)

        self.input_placeholder = QLabel("Type a message")
        self.input_placeholder.setStyleSheet("background: transparent; color: #8696A0; font-size: 11.5px;")
        ip_layout.addWidget(self.input_placeholder)
        bot_layout.addWidget(input_pill, 1)

        # Green Send Button
        self.send_btn = QPushButton("➤")
        self.send_btn.setToolTip("Open in WhatsApp for this student (1-Click)")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setFixedSize(30, 30)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A884;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                font-size: 13px;
                font-weight: bold;
                padding-left: 2px;
            }
            QPushButton:hover {
                background-color: #25D366;
            }
        """)
        self.send_btn.clicked.connect(self.send_clicked.emit)
        bot_layout.addWidget(self.send_btn)

        layout.addWidget(bottom_bar)

    def set_preview(self, text: str, student: Optional[Student], raw_char_count: int = 0):
        """Update live preview with recipient details and rendered message content."""
        self.char_badge.setText(f"{raw_char_count} chars")

        if not student:
            self.avatar_lbl.setText("?")
            self.contact_name_lbl.setText("No Student Selected")
            self.contact_status_lbl.setText("Select a student from directory")
            self.msg_text_lbl.setText("Select a student from the directory on the left to see live personalized WhatsApp message preview.")
            return

        # Initials for avatar
        parts = (student.name or "").strip().split()
        if len(parts) >= 2:
            initials = (parts[0][0] + parts[1][0]).upper()
        elif len(parts) == 1 and parts[0]:
            initials = parts[0][:2].upper()
        else:
            initials = "ST"

        self.avatar_lbl.setText(initials)
        self.contact_name_lbl.setText(student.name or "Student")
        course_str = f" • {student.course_name}" if student.course_name else ""
        self.contact_status_lbl.setText(f"+91 {student.mobile_no or 'N/A'}{course_str}")

        if not text:
            self.msg_text_lbl.setText("Type a message or select a saved template above to see the WhatsApp preview.")
        else:
            self.msg_text_lbl.setText(text)

        now_str = datetime.now().strftime("%I:%M %p").lstrip("0")
        self.time_lbl.setText(now_str)


class MessagingView(QWidget):
    """Refined and modern UI for WhatsApp message automation, template management, and bulk student dispatch."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.all_students: List[Student] = []
        self.filtered_students: List[Student] = []
        self.selected_student_ids: set = set()
        self.highlighted_student: Optional[Student] = None
        self.templates: List[MessageTemplate] = []

        self._build_ui()
        self.refresh_data()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # 1. Top Header & KPI Summary Bar
        header_card = QFrame()
        header_card.setObjectName("card")
        header_card.setStyleSheet("""
            QFrame#card {
                background-color: #131823;
                border: 1px solid #1F293D;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(14, 10, 14, 10)
        h_layout.setSpacing(12)

        h_info = QVBoxLayout()
        h_info.setSpacing(2)
        title_lbl = QLabel("💬 WhatsApp Automation & Message Workflows")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #F8FAFC;")
        h_info.addWidget(title_lbl)

        sub_lbl = QLabel("Select students, compose personalized templates with smart tags & Spintax, and dispatch via WhatsApp.")
        sub_lbl.setStyleSheet("font-size: 11.5px; color: #94A3B8;")
        h_info.addWidget(sub_lbl)
        h_layout.addLayout(h_info, 3)

        # KPI Badges
        self.stat_total_lbl = QLabel("Total Students: <b>0</b>")
        self.stat_total_lbl.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-size: 11.5px; color: #E2E8F0;")
        h_layout.addWidget(self.stat_total_lbl)

        self.stat_pending_lbl = QLabel("Pending Fees: <b>0</b>")
        self.stat_pending_lbl.setStyleSheet("background-color: #EF444418; border: 1px solid #EF444455; border-radius: 6px; padding: 6px 12px; font-size: 11.5px; color: #F87171; font-weight: 600;")
        h_layout.addWidget(self.stat_pending_lbl)

        self.stat_selected_lbl = QLabel("Selected: <b>0</b>")
        self.stat_selected_lbl.setStyleSheet("background-color: #10B98118; border: 1px solid #10B98155; border-radius: 6px; padding: 6px 12px; font-size: 11.5px; color: #34D399; font-weight: 700;")
        h_layout.addWidget(self.stat_selected_lbl)

        main_layout.addWidget(header_card)

        # 2. Main Two-Column Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1F293D;
                width: 2px;
            }
        """)

        # Left Column: Student Selection Table & Filters
        left_widget = self._build_left_panel()
        splitter.addWidget(left_widget)

        # Right Column: Template Selector, Composer & Live WhatsApp Preview
        right_widget = self._build_right_panel()
        splitter.addWidget(right_widget)

        splitter.setSizes([580, 540])
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

        self.search_bar = SearchBar(placeholder="Search by Name, Mobile, Course, ID...")
        self.search_bar.searched.connect(lambda s: self._apply_filters())
        filter_bar.addWidget(self.search_bar, 3)

        self.course_filter = QComboBox()
        self.course_filter.addItem("All Courses")
        self.course_filter.setMinimumWidth(125)
        self.course_filter.currentTextChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.course_filter, 2)

        self.fee_filter = QComboBox()
        self.fee_filter.addItems(["All Fees", "Pending / Partial", "Fully Paid", "No Fee"])
        self.fee_filter.setMinimumWidth(120)
        self.fee_filter.currentTextChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.fee_filter, 2)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setToolTip("Reload latest students and payments from database")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #CBD5E1;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11.5px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #F8FAFC;
                border-color: #475569;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        filter_bar.addWidget(refresh_btn)

        layout.addLayout(filter_bar)

        # Quick Batch Selection Toolbar
        quick_select_row = QHBoxLayout()
        quick_select_row.setSpacing(6)

        self.btn_select_all = QPushButton("☑️ Select All")
        self.btn_select_all.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F1F5F9;
                border: 1px solid #334155;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11.5px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #475569;
            }
        """)
        self.btn_select_all.clicked.connect(self._select_all_visible)
        quick_select_row.addWidget(self.btn_select_all)

        self.btn_select_pending = QPushButton("🎯 Select Pending Fees (0)")
        self.btn_select_pending.setStyleSheet("""
            QPushButton {
                background-color: #7C2D122A;
                color: #FED7AA;
                border: 1px solid #9A3412;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11.5px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #7C2D1255;
                border-color: #EA580C;
                color: #FFFFFF;
            }
        """)
        self.btn_select_pending.clicked.connect(self._select_pending_fees_only)
        quick_select_row.addWidget(self.btn_select_pending)

        self.btn_deselect = QPushButton("✕ Clear Selection")
        self.btn_deselect.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: 1px solid #334155;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #E2E8F0;
                border-color: #475569;
            }
        """)
        self.btn_deselect.clicked.connect(self._deselect_all)
        quick_select_row.addWidget(self.btn_deselect)

        quick_select_row.addStretch()

        self.table_count_lbl = QLabel("0 students")
        self.table_count_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        quick_select_row.addWidget(self.table_count_lbl)

        layout.addLayout(quick_select_row)

        # Student Selection Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "✓", "Student Name & ID", "Mobile", "Course", "Balance Due", "Last Fee Paid"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0F131C;
                gridline-color: #1A2130;
                border: 1px solid #1F293D;
                border-radius: 6px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px 6px;
                border-bottom: 1px solid #161C28;
            }
            QTableWidget::item:selected {
                background-color: #1E293B;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #161C28;
                color: #94A3B8;
                font-weight: 700;
                font-size: 11px;
                padding: 6px 4px;
                border: none;
                border-bottom: 1px solid #283347;
            }
        """)

        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 52)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 115)
        h.setSectionResizeMode(3, QHeaderView.Stretch)
        h.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 105)
        h.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 165)

        self.table.itemSelectionChanged.connect(self._on_table_row_selected)
        layout.addWidget(self.table, 1)

        return left_container

    def _build_right_panel(self) -> QWidget:
        right_container = QFrame()
        right_container.setObjectName("card")
        layout = QVBoxLayout(right_container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Saved Templates Header Toolbar
        tmpl_card = QFrame()
        tmpl_card.setStyleSheet("background-color: #161C28; border: 1px solid #222C3D; border-radius: 8px; padding: 6px 8px;")
        tmpl_header = QHBoxLayout(tmpl_card)
        tmpl_header.setContentsMargins(4, 2, 4, 2)
        tmpl_header.setSpacing(8)

        t_lbl = QLabel("<b>📁 Template:</b>")
        t_lbl.setStyleSheet("font-size: 12px; color: #F8FAFC;")
        tmpl_header.addWidget(t_lbl)

        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self._on_template_selected)
        self.template_combo.setStyleSheet("""
            QComboBox {
                background-color: #0F131C;
                border: 1px solid #283347;
                border-radius: 6px;
                padding: 4px 10px;
                color: #F8FAFC;
                font-size: 12px;
            }
        """)
        tmpl_header.addWidget(self.template_combo, 1)

        new_tmpl_btn = QPushButton("+ New")
        new_tmpl_btn.setToolTip("Create a new reusable template")
        new_tmpl_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid #0284C7;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11.5px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)
        new_tmpl_btn.clicked.connect(self._create_new_template)
        tmpl_header.addWidget(new_tmpl_btn)

        edit_tmpl_btn = QPushButton("✏️ Edit")
        edit_tmpl_btn.setToolTip("Edit the currently selected template")
        edit_tmpl_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #CBD5E1;
                border: 1px solid #334155;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11.5px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        edit_tmpl_btn.clicked.connect(self._edit_current_template)
        tmpl_header.addWidget(edit_tmpl_btn)

        del_tmpl_btn = QPushButton("🗑️")
        del_tmpl_btn.setToolTip("Delete currently selected template")
        del_tmpl_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F87171;
                border: 1px solid #EF444455;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11.5px;
            }
            QPushButton:hover {
                background-color: #7F1D1D;
                color: #FFFFFF;
            }
        """)
        del_tmpl_btn.clicked.connect(self._delete_current_template)
        tmpl_header.addWidget(del_tmpl_btn)

        layout.addWidget(tmpl_card)

        # 2. Dynamic Merge Tags Pill Toolbar
        tags_bar = QHBoxLayout()
        tags_bar.setSpacing(4)

        t_hint = QLabel("💡 <b>Insert:</b>")
        t_hint.setStyleSheet("font-size: 11px; color: #38BDF8;")
        tags_bar.addWidget(t_hint)

        quick_tags = [
            ("{name}", "Name"),
            ("{course}", "Course"),
            ("{balance_due}", "Balance"),
            ("{last_paid_date}", "Payment Date"),
            ("{days_ago}", "Days Ago"),
            ("{id_no}", "Roll No"),
            ("{Dear|Hello}", "Spintax"),
        ]
        for q_tag, hint in quick_tags:
            btn = QPushButton(q_tag)
            btn.setToolTip(f"Click to insert tag for {hint}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #182234;
                    color: #38BDF8;
                    border: 1px solid #0284C755;
                    border-radius: 4px;
                    padding: 2px 7px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0284C7;
                    color: #FFFFFF;
                    border-color: #0284C7;
                }
            """)
            btn.clicked.connect(lambda checked=False, t=q_tag: self._insert_tag_to_composer(t))
            tags_bar.addWidget(btn)
        tags_bar.addStretch()
        layout.addLayout(tags_bar)

        # 3. Message Composer Text Area
        self.composer_edit = QTextEdit()
        self.composer_edit.setPlaceholderText("Write your WhatsApp message template here using {name}, {course}, {balance_due} and Spintax variations...")
        self.composer_edit.setMinimumHeight(80)
        self.composer_edit.setMaximumHeight(105)
        self.composer_edit.setStyleSheet("""
            QTextEdit {
                background-color: #0C1018;
                border: 1px solid #1F293D;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-family: 'Consolas', 'Segoe UI', monospace;
                color: #F8FAFC;
                line-height: 1.35;
            }
            QTextEdit:focus {
                border: 1px solid #0284C7;
                background-color: #0F1420;
            }
        """)
        self.composer_edit.textChanged.connect(self._update_live_preview)
        layout.addWidget(self.composer_edit)

        # 4. Realistic WhatsApp Chat Simulator
        self.chat_preview = WhatsAppChatPreviewWidget(self)
        self.chat_preview.send_clicked.connect(self._on_single_send_clicked)
        layout.addWidget(self.chat_preview, 1)

        # 5. Bottom Batch Dispatch Action Button
        act_box = QVBoxLayout()
        act_box.setSpacing(6)

        self.start_dispatch_btn = QPushButton("⚡ Start WhatsApp Batch Dispatch (0 Selected)")
        self.start_dispatch_btn.setObjectName("primaryBtn")
        self.start_dispatch_btn.setCursor(Qt.PointingHandCursor)
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
            QPushButton:disabled {
                background-color: #1E293B;
                color: #64748B;
                border-color: #334155;
            }
        """)
        self.start_dispatch_btn.clicked.connect(self._on_start_batch_dispatch)
        act_box.addWidget(self.start_dispatch_btn)

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

        # Load first template into composer if empty
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
        self.table_count_lbl.setText(f"Showing {len(self.filtered_students)} of {len(self.all_students)} students")

        pending_in_filtered = sum(1 for s in self.filtered_students if s.balance_due > 0)
        self.btn_select_pending.setText(f"🎯 Select Pending Fees ({pending_in_filtered})")
        self.btn_select_all.setText(f"☑️ Select All ({len(self.filtered_students)})")

        for row_idx, s in enumerate(self.filtered_students):
            self.table.insertRow(row_idx)
            self.table.setRowHeight(row_idx, 46)

            # 0. Centered Checkbox Cell Widget
            chk_container = QWidget()
            chk_container.setStyleSheet("background: transparent;")
            chk_layout = QHBoxLayout(chk_container)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            chk_layout.setAlignment(Qt.AlignCenter)

            chk = QCheckBox()
            chk.setCursor(Qt.PointingHandCursor)
            chk.setChecked(s.id in self.selected_student_ids)
            chk.setStyleSheet("""
                QCheckBox {
                    background: transparent;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 1.5px solid #475569;
                    background-color: #1E293B;
                }
                QCheckBox::indicator:hover {
                    border-color: #10B981;
                    background-color: #334155;
                }
                QCheckBox::indicator:checked {
                    background-color: #10B981;
                    border-color: #10B981;
                }
            """)
            chk.toggled.connect(lambda checked, sid=s.id: self._on_student_toggled(sid, checked))
            chk_layout.addWidget(chk)
            self.table.setCellWidget(row_idx, 0, chk_container)

            # 1. Student Name & ID (2-Line Widget)
            name_widget = QWidget()
            name_widget.setStyleSheet("background: transparent;")
            n_layout = QVBoxLayout(name_widget)
            n_layout.setContentsMargins(4, 2, 4, 2)
            n_layout.setSpacing(1)
            n_layout.setAlignment(Qt.AlignVCenter)

            n_lbl = QLabel(s.name)
            n_lbl.setStyleSheet("background: transparent; color: #F8FAFC; font-weight: 600; font-size: 12.5px;")
            id_lbl = QLabel(f"ID: {s.id_no}")
            id_lbl.setStyleSheet("background: transparent; color: #64748B; font-size: 10.5px;")

            n_layout.addWidget(n_lbl)
            n_layout.addWidget(id_lbl)
            self.table.setCellWidget(row_idx, 1, name_widget)

            # 2. Mobile Number
            mob_item = QTableWidgetItem(s.mobile_no or "-")
            mob_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, mob_item)

            # 3. Course
            c_item = QTableWidgetItem(s.course_name or "-")
            c_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 3, c_item)

            # 4. Balance Due
            bal = s.balance_due
            bal_str = f"₹{bal:,.0f}" if bal > 0 else "₹0"
            bal_item = QTableWidgetItem(bal_str)
            bal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if bal > 0:
                bal_item.setForeground(Qt.red)
            else:
                bal_item.setForeground(Qt.darkGreen)
            self.table.setItem(row_idx, 4, bal_item)

            # 5. Last Fee Paid
            last_pay_str = s.last_payment_summary
            lp_item = QTableWidgetItem(last_pay_str)
            lp_item.setTextAlignment(Qt.AlignCenter)
            if "No Payment" in last_pay_str:
                lp_item.setForeground(Qt.gray)
            self.table.setItem(row_idx, 5, lp_item)

        if self.filtered_students:
            if not self.highlighted_student or self.highlighted_student not in self.filtered_students:
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
        self._sync_table_checkboxes()
        self._update_selected_count_ui()

    def _select_pending_fees_only(self):
        self.selected_student_ids.clear()
        for s in self.filtered_students:
            if s.balance_due > 0:
                self.selected_student_ids.add(s.id)
        self._sync_table_checkboxes()
        self._update_selected_count_ui()

    def _deselect_all(self):
        self.selected_student_ids.clear()
        self._sync_table_checkboxes()
        self._update_selected_count_ui()

    def _sync_table_checkboxes(self):
        for row_idx, s in enumerate(self.filtered_students):
            cell_widget = self.table.cellWidget(row_idx, 0)
            if cell_widget:
                chk = cell_widget.findChild(QCheckBox)
                if chk:
                    chk.blockSignals(True)
                    chk.setChecked(s.id in self.selected_student_ids)
                    chk.blockSignals(False)

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
        char_count = len(template_text)

        if not self.highlighted_student:
            self.chat_preview.set_preview("", None, char_count)
            return

        s = self.highlighted_student
        if not template_text:
            self.chat_preview.set_preview("", s, char_count)
            return

        rendered = MessageController.render_message(template_text, s, randomize_spintax=True)
        self.chat_preview.set_preview(rendered, s, char_count)

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

        template_text = self.composer_edit.toPlainText().strip()
        if not template_text:
            QMessageBox.warning(self, "Empty Message", "Message content cannot be empty.")
            return

        rendered_msg = MessageController.render_message(template_text, self.highlighted_student, randomize_spintax=True)
        url = MessageController.build_whatsapp_url(self.highlighted_student.mobile_no, rendered_msg, use_desktop_app=True)
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
