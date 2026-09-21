import logging
import os
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

# Core imports
from app.core.config import (
    APP_NAME,
    APP_VERSION,
    DATABASE_PATH,
    LOGS_DIR,
    ROOT_DIR,
)
from app.core.database import init_db, close_db
from app.modules.courses.controllers import CourseController
from app.modules.staff.controllers import StaffController

# Bridge imports
from app.bridge import (
    CRMBridge,
    StudentsBridge,
    CoursesBridge,
    StaffBridge,
    FinanceBridge,
    MessagingBridge,
    ReportsBridge,
    UpdaterBridge,
)

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


def main():
    """Application Entrypoint for Qt Quick / QML Architecture."""
    logger.info("Starting Personal CRM (Qt Quick Architecture)...")

    # 1. Initialize SQLite database
    init_db()

    # 2. Seed standard courses & staff directory if empty
    try:
        CourseController.seed_default_courses_if_empty()
        StaffController.seed_default_staff_if_empty()
    except Exception as e:
        logger.warning(f"Note during initial seeding: {e}")

    # 3. Create PySide6 GUI Application
    # Set environment variables for high-DPI scaling
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("CADDESK Centre")
    app.setFont(QFont("Segoe UI", 10))

    # 4. Instantiate Python Bridge Controllers
    crm_bridge = CRMBridge(app)
    students_bridge = StudentsBridge(app)
    courses_bridge = CoursesBridge(app)
    staff_bridge = StaffBridge(app)
    finance_bridge = FinanceBridge(app)
    messaging_bridge = MessagingBridge(app)
    reports_bridge = ReportsBridge(app)
    updater_bridge = UpdaterBridge(app)

    # 5. Initialize QML Engine & Register Context Properties
    engine = QQmlApplicationEngine()

    ui_dir = PROJECT_ROOT / "ui"
    engine.addImportPath(str(ui_dir))
    engine.addImportPath(str(PROJECT_ROOT))

    context = engine.rootContext()
    context.setContextProperty("crmBridge", crm_bridge)
    context.setContextProperty("studentsBridge", students_bridge)
    context.setContextProperty("coursesBridge", courses_bridge)
    context.setContextProperty("staffBridge", staff_bridge)
    context.setContextProperty("financeBridge", finance_bridge)
    context.setContextProperty("messagingBridge", messaging_bridge)
    context.setContextProperty("reportsBridge", reports_bridge)
    context.setContextProperty("updaterBridge", updater_bridge)

    # 6. Load Master QML Entrypoint
    main_qml_path = ui_dir / "Main.qml"
    if not main_qml_path.exists():
        logger.critical(f"QML entrypoint not found at: {main_qml_path}")
        sys.exit(1)

    engine.load(QUrl.fromLocalFile(str(main_qml_path.resolve())))

    if not engine.rootObjects():
        logger.critical("Failed to load QML root object. Exiting...")
        sys.exit(1)

    # Clean shutdown hook
    app.aboutToQuit.connect(close_db)

    # 7. Start background check for updates
    try:
        updater_bridge.checkForUpdates()
    except Exception as e:
        logger.debug(f"Background update check skipped: {e}")

    logger.info("Personal CRM Application started successfully.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
