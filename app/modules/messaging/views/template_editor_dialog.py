from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.message_template import MessageTemplate
from app.modules.messaging.controllers import MessageController


class TemplateEditorDialog(QDialog):
    """Dialog to create or edit reusable WhatsApp message templates."""

    def __init__(self, template: Optional[MessageTemplate] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.template = template
        self.is_edit = template is not None

        self.setWindowTitle("Edit Saved Message Template" if self.is_edit else "Create New Message Template")
        self.setMinimumSize(560, 480)
        self.resize(620, 520)

        self._build_ui()
        if self.is_edit and self.template:
            self._load_template_data()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Header Title
        h_title = QLabel("💬 Message Template Editor")
        h_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        main_layout.addWidget(h_title)

        desc = QLabel(
            "Use merge tags like <b>{name}</b>, <b>{course}</b>, <b>{balance_due}</b> and Spintax variations "
            "like <b>{Dear|Hello|Respected}</b> to automatically personalize each message."
        )
        desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        desc.setWordWrap(True)
        main_layout.addWidget(desc)

        # Form fields
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #161A23; border: 1px solid #283042; border-radius: 8px; padding: 12px;")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(10)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Fee Reminder - 2nd Installment")
        form_layout.addRow(QLabel("<b>Template Title:</b>"), self.title_input)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Fees", "Admissions", "Batches", "General", "Exams"])
        self.category_combo.setEditable(True)
        form_layout.addRow(QLabel("<b>Category:</b>"), self.category_combo)

        main_layout.addWidget(form_frame)

        # Merge Tags Quick-Insert Bar
        tags_box = QFrame()
        tags_box.setStyleSheet("background-color: #12151D; border: 1px dashed #334155; border-radius: 6px; padding: 6px;")
        t_layout = QVBoxLayout(tags_box)
        t_layout.setSpacing(6)
        t_layout.setContentsMargins(6, 6, 6, 6)

        t_lbl = QLabel("<b>Quick Insert Tags & Variations:</b>")
        t_lbl.setStyleSheet("font-size: 11px; color: #38BDF8;")
        t_layout.addWidget(t_lbl)

        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(6)
        tag_buttons = [
            ("{name}", "Full Name"),
            ("{course}", "Course"),
            ("{balance_due}", "Balance (₹)"),
            ("{last_paid_date}", "Last Paid Date"),
            ("{days_ago}", "Days Elapsed"),
            ("{id_no}", "Student ID"),
        ]
        for tag, hint in tag_buttons:
            btn = QPushButton(tag)
            btn.setToolTip(f"Inserts {hint}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    color: #38BDF8;
                    border: 1px solid #0284C7;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0284C7;
                    color: #FFFFFF;
                }
            """)
            btn.clicked.connect(lambda checked=False, t=tag: self._insert_tag(t))
            btn_row1.addWidget(btn)
        btn_row1.addStretch()
        t_layout.addLayout(btn_row1)

        # Spintax Helper Button
        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(6)
        spintax_samples = [
            ("{Dear|Hello|Respected}", "Greeting Variation"),
            ("{your fee balance of ₹{balance_due} is pending|kindly settle your pending fee of ₹{balance_due}}", "Fee Text Variation"),
        ]
        for sp, hint in spintax_samples:
            s_btn = QPushButton(f"🎲 {sp[:24]}...")
            s_btn.setToolTip(f"Spintax: {hint}")
            s_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    color: #F59E0B;
                    border: 1px solid #D97706;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #D97706;
                    color: #FFFFFF;
                }
            """)
            s_btn.clicked.connect(lambda checked=False, t=sp: self._insert_tag(t))
            btn_row2.addWidget(s_btn)
        btn_row2.addStretch()
        t_layout.addLayout(btn_row2)

        main_layout.addWidget(tags_box)

        # Message Content Editor
        main_layout.addWidget(QLabel("<b>Message Template Text:</b>"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Type your WhatsApp message template here...")
        self.content_edit.setMinimumHeight(130)
        self.content_edit.setStyleSheet("font-family: 'Consolas', 'Segoe UI', monospace; font-size: 12px;")
        main_layout.addWidget(self.content_edit)

        # Dialog Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Save Template")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        main_layout.addLayout(btn_layout)

    def _insert_tag(self, tag_text: str):
        self.content_edit.insertPlainText(tag_text)
        self.content_edit.setFocus()

    def _load_template_data(self):
        if not self.template:
            return
        self.title_input.setText(self.template.title or "")
        self.category_combo.setCurrentText(self.template.category or "General")
        self.content_edit.setPlainText(self.template.content or "")

    def _on_save(self):
        title = self.title_input.text().strip()
        content = self.content_edit.toPlainText().strip()
        category = self.category_combo.currentText().strip()

        if not title:
            QMessageBox.warning(self, "Validation Error", "Please provide a Template Title.")
            self.title_input.setFocus()
            return

        if not content:
            QMessageBox.warning(self, "Validation Error", "Message template content cannot be empty.")
            self.content_edit.setFocus()
            return

        data = {
            "title": title,
            "category": category,
            "content": content,
        }

        try:
            if self.is_edit and self.template:
                MessageController.update_template(self.template.id, data)
            else:
                MessageController.create_template(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save message template: {e}")
