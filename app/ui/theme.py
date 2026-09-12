"""
Ultra-Modern Dark Theme for PySide6 Desktop CRM.
Engineered with refined obsidian palette, smooth card borders, glowing focus states,
seamless table layouts, and ultra-clean typography.
"""

DARK_THEME_QSS = """
/* Global Application Reset */
QWidget {
    background-color: #0B0E14;
    color: #F1F5F9;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

/* Main Window, Dialogs & Frames */
QMainWindow, QDialog {
    background-color: #0B0E14;
}

QFrame#card, QFrame.card {
    background-color: #131823;
    border: 1px solid #1F293D;
    border-radius: 12px;
}

QFrame#sidebar {
    background-color: #090B10;
    border-right: 1px solid #1A2130;
}

/* Section & Card Headers */
QLabel#headerTitle {
    font-size: 19px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.3px;
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
    margin-bottom: 2px;
}

QLabel#statValue {
    font-size: 24px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}

QLabel#statLabel {
    font-size: 12px;
    color: #94A3B8;
    font-weight: 500;
}

/* Form Labels */
QLabel#fieldLabel, QLabel {
    color: #CBD5E1;
}

/* Modern Input Controls */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #181E2C;
    color: #F8FAFC;
    border: 1px solid #283347;
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 20px;
    font-size: 13px;
}

QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QTextEdit:hover {
    border: 1px solid #3B4A66;
    background-color: #1B2232;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 1.5px solid #3B82F6;
    background-color: #1D2536;
}

QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled {
    background-color: #10141D;
    color: #64748B;
    border-color: #1F2736;
}

/* Dropdown styling */
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #283347;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}

QComboBox QAbstractItemView {
    background-color: #181E2C;
    color: #F8FAFC;
    border: 1px solid #3B82F6;
    border-radius: 8px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    padding: 6px;
    outline: none;
}

/* Buttons */
QPushButton {
    background-color: #1E2536;
    color: #F1F5F9;
    border: 1px solid #2D3950;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #2A344A;
    border-color: #3F4F6D;
}

QPushButton:pressed {
    background-color: #161C28;
}

/* Primary Brand Button */
QPushButton#primaryBtn, QPushButton.primary {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #1D4ED8;
    font-weight: 600;
}

QPushButton#primaryBtn:hover, QPushButton.primary:hover {
    background-color: #3B82F6;
    border-color: #2563EB;
}

QPushButton#primaryBtn:pressed, QPushButton.primary:pressed {
    background-color: #1D4ED8;
}

/* Success Button */
QPushButton#successBtn, QPushButton.success {
    background-color: #059669;
    color: #FFFFFF;
    border: 1px solid #047857;
    font-weight: 600;
}

QPushButton#successBtn:hover, QPushButton.success:hover {
    background-color: #10B981;
    border-color: #059669;
}

/* Danger Button */
QPushButton#dangerBtn, QPushButton.danger {
    background-color: #DC2626;
    color: #FFFFFF;
    border: 1px solid #B91C1C;
    font-weight: 600;
}

QPushButton#dangerBtn:hover, QPushButton.danger:hover {
    background-color: #EF4444;
    border-color: #DC2626;
}

/* Modern Tables */
QTableWidget, QTableView {
    background-color: #131823;
    border: 1px solid #1F293D;
    border-radius: 10px;
    gridline-color: #1A2232;
    color: #F1F5F9;
    selection-background-color: #1E293B;
    selection-color: #FFFFFF;
    outline: none;
}

QHeaderView::section {
    background-color: #0F131C;
    color: #94A3B8;
    padding: 10px 8px;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-bottom: 1.5px solid #1F293D;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #171E2C;
}

QTableWidget::item:selected {
    background-color: #1E293B;
}

/* Smooth Modern Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 7px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #2D3748;
    min-height: 24px;
    border-radius: 3.5px;
}

QScrollBar::handle:vertical:hover {
    background: #4A5568;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 7px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #2D3748;
    min-width: 24px;
    border-radius: 3.5px;
}

QScrollBar::handle:horizontal:hover {
    background: #4A5568;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* CheckBoxes & RadioButtons */
QCheckBox, QRadioButton {
    spacing: 8px;
    color: #E2E8F0;
    font-size: 13px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    background-color: #181E2C;
    border: 1px solid #2E3A4E;
    border-radius: 5px;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #3B82F6;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border-color: #3B82F6;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #1F293D;
    background-color: #131823;
    border-radius: 10px;
    padding: 14px;
}

QTabBar::tab {
    background-color: #0E121A;
    color: #94A3B8;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
}

QTabBar::tab:hover {
    background-color: #151A24;
    color: #E2E8F0;
}

QTabBar::tab:selected {
    background-color: #131823;
    color: #3B82F6;
    font-weight: 600;
    border-bottom: 2px solid #3B82F6;
}

/* ========================================================================= */
/* Modern Dark QCalendarWidget Styles (Fixed Layout, High Contrast, No Cutoff)*/
/* ========================================================================= */
QCalendarWidget {
    background-color: #111622;
    border: 1.5px solid #283347;
    border-radius: 10px;
    min-width: 320px;
    min-height: 280px;
}

/* Calendar Navigation Bar (Top Header) */
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #0B0E14;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    border-bottom: 1px solid #1F293D;
    min-height: 42px;
    padding: 2px 6px;
}

/* Month & Navigation Buttons */
QCalendarWidget QToolButton {
    background-color: #181E2C;
    color: #F8FAFC;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #2D3950;
    border-radius: 6px;
    margin: 2px;
    padding: 4px 10px;
    min-height: 24px;
}

QCalendarWidget QToolButton:hover {
    background-color: #2563EB;
    border-color: #3B82F6;
    color: #FFFFFF;
}

QCalendarWidget QToolButton:pressed {
    background-color: #1D4ED8;
}

QCalendarWidget QToolButton#qt_calendar_prevmonth,
QCalendarWidget QToolButton#qt_calendar_nextmonth {
    min-width: 32px;
    font-size: 15px;
    font-weight: bold;
    qproperty-icon: none;
}

/* Year SpinBox */
QCalendarWidget QSpinBox {
    background-color: #181E2C;
    color: #F8FAFC;
    border: 1px solid #2D3950;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    margin: 2px;
    padding: 4px 8px;
    min-width: 70px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {
    width: 16px;
    background-color: #222B3D;
    border-radius: 3px;
}

/* Month Dropdown Menu */
QCalendarWidget QMenu {
    background-color: #131823;
    color: #F8FAFC;
    border: 1px solid #283347;
    border-radius: 8px;
    padding: 6px;
}

QCalendarWidget QMenu::item {
    padding: 6px 16px;
    border-radius: 4px;
}

QCalendarWidget QMenu::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
}

/* Calendar Days Table View */
QCalendarWidget QTableView {
    background-color: #111622;
    border: none;
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
    gridline-color: transparent;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    font-size: 13px;
    font-weight: 500;
    outline: none;
    padding: 6px;
}

/* Weekday Header (Mon, Tue, Wed...) */
QCalendarWidget QTableView QHeaderView::section {
    background-color: #111622;
    color: #94A3B8;
    font-weight: 700;
    font-size: 11px;
    padding: 8px 2px;
    border: none;
    border-bottom: 1px solid #1F293D;
}

/* Active & Inactive Day Cells */
QCalendarWidget QAbstractItemView:enabled {
    color: #F1F5F9;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #475569;
}
"""

def apply_theme(app):
    """Applies the custom modern theme to the QApplication."""
    app.setStyleSheet(DARK_THEME_QSS)
