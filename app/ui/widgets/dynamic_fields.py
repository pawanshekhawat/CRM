from datetime import date, datetime
from typing import Dict, List
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QWidget,
)

from app.models.custom_fields import CustomFieldDefinition

class DynamicFieldsWidget(QWidget):
    """Dynamically generates input fields based on CustomFieldDefinition list."""

    def __init__(self, definitions: List[CustomFieldDefinition], parent=None):
        super().__init__(parent)
        self.definitions = definitions
        self.field_widgets: Dict[str, QWidget] = {}

        self.form_layout = QFormLayout(self)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)

        self._build_fields()

    def _build_fields(self):
        if not self.definitions:
            no_fields_lbl = QLabel("No custom fields defined. Click 'Manage Custom Fields' to add custom inputs.")
            no_fields_lbl.setStyleSheet("color: #64748B; font-style: italic;")
            self.form_layout.addRow(no_fields_lbl)
            return

        for df in self.definitions:
            label_text = df.field_label + (" *" if df.is_required else "")
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 500; color: #CBD5E1;")

            widget = self._create_field_widget(df)
            self.field_widgets[df.id] = widget
            self.form_layout.addRow(label, widget)

    def _create_field_widget(self, df: CustomFieldDefinition) -> QWidget:
        f_type = (df.field_type or "text").lower()

        if f_type == "number":
            w = QDoubleSpinBox()
            w.setRange(-99999999, 99999999)
            w.setDecimals(2)
            return w

        elif f_type == "date":
            w = QDateEdit()
            w.setCalendarPopup(True)
            w.setDisplayFormat("dd/MM/yyyy")
            w.setDate(QDate.currentDate())
            return w

        elif f_type == "select":
            w = QComboBox()
            w.addItem("-- Select --", "")
            for opt in df.get_options():
                w.addItem(opt, opt)
            return w

        elif f_type == "checkbox":
            w = QCheckBox("Yes")
            return w

        elif f_type == "textarea":
            w = QTextEdit()
            w.setMaximumHeight(70)
            return w

        else: # text default
            w = QLineEdit()
            return w

    def get_values(self) -> Dict[str, str]:
        """Returns a mapping of field_id -> str value."""
        values = {}
        for df in self.definitions:
            widget = self.field_widgets.get(df.id)
            if not widget:
                continue

            f_type = (df.field_type or "text").lower()

            if f_type == "number":
                values[df.id] = str(widget.value())
            elif f_type == "date":
                qdate = widget.date()
                values[df.id] = qdate.toString("yyyy-MM-dd")
            elif f_type == "select":
                values[df.id] = widget.currentData() or widget.currentText()
            elif f_type == "checkbox":
                values[df.id] = "true" if widget.isChecked() else "false"
            elif f_type == "textarea":
                values[df.id] = widget.toPlainText().strip()
            else:
                values[df.id] = widget.text().strip()

        return values

    def set_values(self, values: Dict[str, str]):
        """Populates the inputs with existing values."""
        for df in self.definitions:
            val = values.get(df.id)
            if val is None:
                continue

            widget = self.field_widgets.get(df.id)
            if not widget:
                continue

            f_type = (df.field_type or "text").lower()

            if f_type == "number":
                try:
                    widget.setValue(float(val))
                except Exception:
                    pass
            elif f_type == "date":
                try:
                    dt = datetime.strptime(val, "%Y-%m-%d")
                    widget.setDate(QDate(dt.year, dt.month, dt.day))
                except Exception:
                    pass
            elif f_type == "select":
                idx = widget.findText(val)
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            elif f_type == "checkbox":
                widget.setChecked(val.lower() in ("true", "1", "yes"))
            elif f_type == "textarea":
                widget.setPlainText(val)
            else:
                widget.setText(val)
