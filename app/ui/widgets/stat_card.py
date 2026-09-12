from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

class StatCard(QFrame):
    """Modern Dashboard KPI Metric Card with clean responsive spacing."""

    def __init__(self, title: str, value: str = "0", subtitle: str = "", icon: str = "📊", accent_color: str = "#3B82F6", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(84)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Left Info Column
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statLabel")
        self.title_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #94A3B8;")
        info_layout.addWidget(self.title_label)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        self.value_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.3px;")
        info_layout.addWidget(self.value_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setStyleSheet("font-size: 11px; color: #64748B;")
            info_layout.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None

        layout.addLayout(info_layout, 4)

        # Right Icon Container
        icon_box = QFrame()
        icon_box.setFixedSize(42, 42)
        icon_box.setStyleSheet(f"""
            background-color: {accent_color}18;
            border: 1px solid {accent_color}40;
            border-radius: 9px;
        """)
        icon_layout = QVBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 18px; color: {accent_color}; background: transparent; border: none;")
        icon_layout.addWidget(icon_lbl)

        layout.addWidget(icon_box, 1)

    def set_value(self, value: str, subtitle: str = ""):
        self.value_label.setText(value)
        if subtitle and self.subtitle_label:
            self.subtitle_label.setText(subtitle)
