import os
import sys
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QFont
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from app.core.database import init_db
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


def test_qml_engine_loads_all_pages():
    """Verify that QQmlApplicationEngine compiles and initializes Main.qml and all pages without error."""
    init_db()

    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    crm_bridge = CRMBridge(app)
    students_bridge = StudentsBridge(app)
    courses_bridge = CoursesBridge(app)
    staff_bridge = StaffBridge(app)
    finance_bridge = FinanceBridge(app)
    messaging_bridge = MessagingBridge(app)
    reports_bridge = ReportsBridge(app)
    updater_bridge = UpdaterBridge(app)

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

    main_qml = ui_dir / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(main_qml.resolve())))

    root_objs = engine.rootObjects()
    assert len(root_objs) > 0, "QML engine failed to load Main.qml"
    window = root_objs[0]
    assert window is not None
