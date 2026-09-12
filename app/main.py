import logging
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

# Core imports
from app.core.config import APP_NAME, APP_VERSION, DATABASE_PATH, LOGS_DIR, ROOT_DIR
from app.core.database import init_db, close_db
from app.modules.registry import module_registry
from app.modules.students.student_module import StudentModule
from app.modules.staff.staff_module import StaffModule
from app.modules.courses.course_module import CourseModule
from app.ui.theme import apply_theme


# Configure logging strictly to USB logs directory
log_file = LOGS_DIR / "crm.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(str(log_file), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("CRM.Main")

class MainWindow(QMainWindow):
    """Main Application Window with pluggable sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)

        self.module_buttons = {}

        # Main Layout Structure
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar = self._build_sidebar()
        main_layout.addWidget(self.sidebar)

        # 2. Right Content Area (Top bar + Module Stack)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = self._build_top_bar()
        content_layout.addWidget(top_bar)

        # Module Stack
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        main_layout.addWidget(content_container)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Running in isolated USB mode | Database: {DATABASE_PATH.name}")

        # Mount Modules
        self._load_registered_modules()

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(12)

        # Brand / Institute Logo Header
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)

        app_title = QLabel("CADDESK")
        app_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #EF4444; letter-spacing: 1px;")
        brand_layout.addWidget(app_title)

        app_sub = QLabel("CENTRE • Personal CRM")
        app_sub.setStyleSheet("font-size: 11px; color: #94A3B8; font-weight: 600;")
        brand_layout.addWidget(app_sub)

        layout.addLayout(brand_layout)
        layout.addSpacing(16)

        # Modules Navigation Title
        nav_label = QLabel("MODULES")
        nav_label.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 1px;")
        layout.addWidget(nav_label)

        # Container for module buttons
        self.nav_button_container = QVBoxLayout()
        self.nav_button_container.setSpacing(6)
        layout.addLayout(self.nav_button_container)

        layout.addStretch()

        # USB Isolation Badge in Sidebar
        usb_info = QFrame()
        usb_info.setStyleSheet("background-color: #161A23; border: 1px solid #283042; border-radius: 8px; padding: 8px;")
        u_layout = QVBoxLayout(usb_info)
        u_layout.setContentsMargins(8, 8, 8, 8)
        u_layout.setSpacing(4)

        u_title = QLabel("🔒 USB Portable Mode")
        u_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #10B981; border: none; background: transparent;")
        u_layout.addWidget(u_title)

        u_desc = QLabel("All records & files stay strictly on this drive.")
        u_desc.setStyleSheet("font-size: 10px; color: #64748B; border: none; background: transparent;")
        u_desc.setWordWrap(True)
        u_layout.addWidget(u_desc)

        layout.addWidget(usb_info)

        return sidebar

    def _build_top_bar(self) -> QFrame:
        top_bar = QFrame()
        top_bar.setFixedHeight(58)
        top_bar.setStyleSheet("background-color: #12141A; border-bottom: 1px solid #222736;")

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        self.page_title = QLabel("Students & Admissions")
        self.page_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F8FAFC;")
        layout.addWidget(self.page_title)

        layout.addStretch()

        # System / Institute Info Chip
        inst_chip = QLabel("Skill India • MSME Registered")
        inst_chip.setStyleSheet("background-color: #1E2330; border: 1px solid #333C4E; border-radius: 12px; padding: 4px 12px; font-size: 11px; color: #94A3B8;")
        layout.addWidget(inst_chip)

        return top_bar

    def _load_registered_modules(self):
        """Discovers all modules from registry and adds them to navigation & stack."""
        modules = module_registry.get_all_modules()

        for idx, mod in enumerate(modules):
            # Create View Widget
            widget = mod.create_widget(parent=self.stack)
            self.stack.addWidget(widget)

            # Create Nav Button
            btn = QPushButton(f"{mod.module_icon}  {mod.module_name}")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px 14px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: 500;
                    border: none;
                    background-color: transparent;
                    color: #94A3B8;
                }
                QPushButton:hover {
                    background-color: #1E2330;
                    color: #F1F5F9;
                }
                QPushButton:checked {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    font-weight: 600;
                }
            """)
            btn.clicked.connect(lambda checked=False, index=idx, m_name=mod.module_name: self._switch_module(index, m_name))
            self.nav_button_container.addWidget(btn)
            self.module_buttons[mod.module_id] = btn

            if idx == 0:
                btn.setChecked(True)
                self.stack.setCurrentIndex(0)
                self.page_title.setText(mod.module_name)

    def _switch_module(self, index: int, module_name: str):
        self.stack.setCurrentIndex(index)
        self.page_title.setText(module_name)

    def closeEvent(self, event):
        """Clean shutdown handler."""
        logger.info("Application exiting... Checkpointing SQLite database.")
        close_db()
        module_registry.shutdown_all()
        event.accept()

def main():
    """Application Entrypoint."""
    # Ensure database initialized
    init_db()

    # Register default modules
    module_registry.register(StudentModule())
    module_registry.register(StaffModule())
    module_registry.register(CourseModule())
    module_registry.initialize_all()

    # Initialize PySide6 Application
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    apply_theme(app)

    window = MainWindow()
    window.show()

    logger.info("Personal CRM Application started successfully.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
